# urls.py

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import PropertyCreateView, PropertyImageCreateView, PropertyVideoCreateView, HomeView, get_user_details, \
    UserPropertiesListView, PropertyListView, SendVerificationCodeView, VerifyVerificationCodeView

urlpatterns = [
    path('property/', PropertyCreateView.as_view(), name='property-list-create'),
    path('properties/<int:property_id>/images/', PropertyImageCreateView.as_view(), name='property-image-create'),
    path('properties/<int:property_id>/videos/', PropertyVideoCreateView.as_view(), name='property-video-create'),
    path('', HomeView.as_view(), name='home'),
    path('user-details/', get_user_details, name='get_user_details'),
    path('user/properties/', UserPropertiesListView.as_view(), name='user-properties-list'),
    path('property-filter/', PropertyListView.as_view(), name='property-list'),
    path('send-verification-code/', SendVerificationCodeView.as_view(), name='send_verification_code'),
    path('verify-verification-code/', VerifyVerificationCodeView.as_view(), name='verify_verification_code'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)