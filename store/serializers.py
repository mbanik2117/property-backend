# serializers.py

from rest_framework import serializers
from .models import Property, PropertyImage, PropertyVideo
from accounts.models import CustomUser


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image', 'user', 'created_at']

        # Make 'user' read-only so that it's not included during creation
        read_only_fields = ['user']


class PropertyVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVideo
        fields = ['id', 'video']


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    videos = PropertyVideoSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'content', 'city', 'area', 'locality', 'floor', 'property_type',
            'transaction_type','option', 'price', 'area_sqft', 'owner_name', 'contact_number',
            'facing_direction', 'status', 'created_at', 'user', 'images', 'videos'
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name']
