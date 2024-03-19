from django.urls import path

from store.views import SendVerificationCodeView, VerifyVerificationCodeView
from .views import user_signup, user_login, user_logout, check_auth, verify_signup, resend_verification_code, \
    verify_login
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('signup/', csrf_exempt(user_signup), name='user-signup'),
    path('login/', user_login, name='user-login'),
    path('logout/', user_logout, name='user-logout'),
    path('check-auth/', check_auth, name='check-auth'),
    path('verify-signup/', verify_signup, name='verify_signup'),
    path('resend-verification/', resend_verification_code, name='resend_verification_code'),
    path('verify-login/', verify_login, name='verify_login'),

]
