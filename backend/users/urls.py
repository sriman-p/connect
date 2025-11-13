from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    LogoutView,
    UserProfileView,
    PasswordChangeView,
    EmailVerificationView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    health_check,
)

app_name = 'users'

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),

    # Authentication
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Profile
    path('auth/profile/', UserProfileView.as_view(), name='profile'),

    # Password
    path('auth/password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Email
    path('auth/email/verify/', EmailVerificationView.as_view(), name='email-verify'),
]
