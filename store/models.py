from django.db import models
from accounts.models import CustomUser


class Property(models.Model):
    PROPERTY_TYPES = [
        ('house', 'Residential House'),
        ('apartment', 'Apartment'),
        ('society', 'Cooperative Society'),
        ('plot', 'Plot'),
        ('land', 'Land'),
        ('builder_floor', 'Builder Floor'),
    ]

    TRANSACTION_TYPES = [
        ('lease_hold', 'Lease Hold'),
        ('free_hold', 'Free Hold'),
    ]

    DIRECTION_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('ready_to_move', 'Ready to Move'),
        ('under_construction', 'Under Construction'),
    ]

    OPTION = [
        ('sell','SELL'),
        ('rent', 'RENT'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    option = models.CharField(max_length=10, choices = OPTION, default='rent')
    title = models.CharField(max_length=255, default="Default Title")
    content = models.TextField()
    city = models.CharField(max_length=100, default="Default City")
    area = models.IntegerField(default=0)
    locality = models.CharField(max_length=100, default="Default Locality")
    floor = models.IntegerField(default=1)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='apartment')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='free_hold')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    area_sqft = models.IntegerField(default=0)
    owner_name = models.CharField(max_length=255, default="Default Owner")
    contact_number = models.CharField(max_length=50, default="Default Contact Number")
    facing_direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='north')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready_to_move')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} by {self.user.email} - {self.created_at}'


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)  # Include the user field
    image = models.ImageField(upload_to='property_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for Property {self.property_id}'


class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, related_name='videos', on_delete=models.CASCADE, null=True)
    video = models.FileField(upload_to='property_videos/')

    def __str__(self):
        return f'Video for Property {self.property_id}'
