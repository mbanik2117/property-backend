import random

from rest_framework import status, generics, permissions
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout

from .models import CustomUser
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from accounts.task_1 import send_signup_verification, send_signup_email, send_login_verification


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # Use an empty list to disable JWT and session authentication
def user_signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generate a 6-digit random code
        verification_code = str(random.randint(100000, 999999))

        # Store the verification code in the user object
        user.verification_code = verification_code
        user.save()

        # Call the Celery task to send the verification code asynchronously
        send_signup_verification.apply_async(args=[user.id, verification_code])

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # Use an empty list to disable JWT and session authentication
def verify_signup(request):
    email = request.data.get('email', '')
    verification_code = request.data.get('verification_code', '')

    user = get_object_or_404(CustomUser, email=email)

    # Check if the entered code matches the stored verification code
    if verification_code == user.verification_code:
        user.is_verified = True
        user.save()

        # Your logic for sending signup verification response
        response_data = {'message': 'Signup verification successful'}
        send_signup_email.apply_async(args=[user.id])
        return Response(response_data, status=status.HTTP_200_OK)
    else:

        # Handle code mismatch, you can display an error message
        response_data = {'error': 'Invalid verification code'}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_code(request):
    email = request.data.get('email', '')

    user = get_object_or_404(CustomUser, email=email)

    # Generate a new 6-digit random code
    new_verification_code = str(random.randint(100000, 999999))

    # Update the user object with the new verification code
    user.verification_code = new_verification_code
    user.save()

    # Call the Celery task to send the new verification code asynchronously
    send_signup_verification.apply_async(args=[user.id, new_verification_code])

    return Response({'message': 'Verification code resent successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # Use an empty list to disable JWT and session authentication
def user_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, email=email, password=password)

    if user is not None:
        # Generate a 6-digit random code for login verification
        verification_code = str(random.randint(100000, 999999))

        # Store the verification code in the user object
        user.login_verification_code = verification_code
        user.save()

        # Call the Celery task to send the login verification code asynchronously
        send_login_verification.apply_async(args=[user.id, verification_code])

        return Response({'message': 'Verification code sent successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_login(request):
    email = request.data.get('email', '')
    verification_code = request.data.get('verification_code', '')

    user = get_object_or_404(CustomUser, email=email)

    # Check if the entered code matches the stored login verification code
    if verification_code == user.login_verification_code:
        # Clear the login verification code after successful verification
        user.login_verification_code = None
        user.save()

        # Log in the user
        login(request, user)

        # Generate access token and refresh token
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login verification successful',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }, status=status.HTTP_200_OK)
    else:
        # Handle code mismatch, you can display an error message
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([])
@authentication_classes([JWTAuthentication])
def user_logout(request):
    refresh_token = request.data.get('refresh_token')

    if refresh_token:
        try:
            # Decode the refresh token to check its type
            decoded_token = RefreshToken(refresh_token, verify=False)

            # Check if the token is a refresh token
            if decoded_token['token_type'] != 'refresh':
                raise TokenError(
                    {'token_class': 'RefreshToken', 'token_type': 'refresh', 'message': 'Token has wrong type'})

            # Revoke the refresh token by setting its expiration time to the past
            refresh_token_instance = RefreshToken(refresh_token)
            refresh_token_instance.set_exp(0)

            # Logout the user (optional, depending on your authentication mechanism)
            logout(request)

            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Refresh token is required for logout'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])  # Use an empty list to disable JWT and session authentication
def check_auth(request):
    user = request.user
    return Response({'authenticated': True})
