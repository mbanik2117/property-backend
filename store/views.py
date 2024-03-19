import string

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Property, PropertyImage, PropertyVideo
from .serializers import PropertySerializer, PropertyImageSerializer, PropertyVideoSerializer
from .serializers import CustomUserSerializer
from rest_framework import status
from django.db import transaction
from accounts.models import CustomUser
from store.task_2 import send_property_post_email, send_contact_verification_email, send_contact_details_email
import random


class PropertyCreateView(generics.CreateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            data['user'] = request.user.id  # Assign the current user to the 'user' field

            # Separate image and video data
            image_data = data.pop('images', [])
            video_data = data.pop('videos', [])

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                property_instance = self.perform_create(serializer, image_data, video_data)

            # Send property post email asynchronously
            send_property_post_email.apply_async(args=[property_instance.id], countdown=5)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            # Log the exception with traceback
            import traceback
            traceback.print_exc()

            # Return a detailed error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer, image_data, video_data):
        property_instance = serializer.save()

        # Save images
        for image in image_data:
            image_serializer = PropertyImageSerializer(data={'image': image, 'property': property_instance.id})
            image_serializer.is_valid(raise_exception=True)
            image_serializer.save(user=self.request.user)

        # Save videos
        for video in video_data:
            video_serializer = PropertyVideoSerializer(data={'video': video, 'property': property_instance.id})
            video_serializer.is_valid(raise_exception=True)
            video_serializer.save(user=self.request.user)

        return property_instance


class PropertyImageCreateView(generics.CreateAPIView):
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        property_id = self.kwargs['property_id']
        property_instance = Property.objects.get(pk=property_id)
        self.check_object_permissions(self.request, property_instance)

        # Set the user field directly
        serializer.save(property=property_instance, user=self.request.user)

    def post(self, request, *args, **kwargs):
        try:
            property_id = kwargs['property_id']
            property_instance = Property.objects.get(pk=property_id)
            self.check_object_permissions(self.request, property_instance)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)

        return super().post(request, *args, **kwargs)


class PropertyVideoCreateView(generics.CreateAPIView):
    serializer_class = PropertyVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        property_id = self.kwargs['property_id']
        property_instance = Property.objects.get(pk=property_id)
        self.check_object_permissions(self.request, property_instance)
        serializer.save(property=property_instance, user=self.request.user)

    def post(self, request, *args, **kwargs):
        try:
            property_id = kwargs['property_id']
            property_instance = Property.objects.get(pk=property_id)
            self.check_object_permissions(self.request, property_instance)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)

        return super().post(request, *args, **kwargs)


class HomeView(generics.ListAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_details(request):
    user = request.user
    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserPropertiesListView(generics.ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Property.objects.filter(user=user)


class PropertyListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['city', 'locality', 'property_type', 'option']  # Add searchable fields

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by query params
        city = self.request.query_params.get('city')
        locality = self.request.query_params.get('locality')
        property_type = self.request.query_params.get('property_type')
        option = self.request.query_params.get('option')

        if city:
            queryset = queryset.filter(city__iexact=city.lower())  # Case-insensitive city search
        if locality:
            queryset = queryset.filter(locality__iexact=locality.lower())  # Case-insensitive locality search
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if option:
            queryset = queryset.filter(option=option)

        return queryset


class SendVerificationCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Generate an 8-digit verification code
            verification_code = ''.join(random.choices(string.digits, k=6))

            # Associate verification code with the current user
            request.user.contact_verification_code = verification_code
            request.user.save()

            # Call your Celery task asynchronously
            send_contact_verification_email.apply_async(args=[request.user.email, verification_code])

            return Response({'detail': 'Verification code sent successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception with traceback
            import traceback
            traceback.print_exc()

            # Return a detailed error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyVerificationCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            email = request.user.email
            verification_code = request.data.get('verification_code', '')

            try:
                user = CustomUser.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the entered code matches the stored verification code
            if verification_code == user.contact_verification_code:
                # Your logic for successful verification
                response_data = {'message': 'Verification successful'}

                # Get the property ID from request data or any other source
                property_id = request.data.get('property_id', None)
                if property_id is not None:
                    # Ensure property_id is converted to integer before passing
                    send_contact_details_email.apply_async(args=[email, int(property_id)])  # Pass user_email as the first argument
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Property ID is missing'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Handle code mismatch, you can display an error message
                response_data = {'error': 'Invalid verification code'}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the exception with traceback
            import traceback
            traceback.print_exc()

            # Return a detailed error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)