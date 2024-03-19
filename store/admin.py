from django.contrib import admin
from .models import Property, PropertyImage, PropertyVideo


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


class PropertyVideoInline(admin.TabularInline):
    model = PropertyVideo
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('user', 'property_type', 'transaction_type', 'status', 'option')  # Remove 'option' from list_filter
    search_fields = ('title', 'user__email', 'city', 'locality', 'owner_name')
    inlines = [PropertyImageInline, PropertyVideoInline]


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('property__title', 'user__email')


@admin.register(PropertyVideo)
class PropertyVideoAdmin(admin.ModelAdmin):
    list_display = ('property',)
    search_fields = ('property__title',)
