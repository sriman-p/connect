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
    PasskeyRegistrationInitView,
    PasskeyRegistrationCompleteView,
    PasskeyAuthenticationInitView,
    PasskeyAuthenticationCompleteView,
    PasskeyCredentialListView,
    PasskeyCredentialDeleteView,
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

    # Passkey Authentication
    path('auth/passkey/register/init/', PasskeyRegistrationInitView.as_view(), name='passkey-register-init'),
    path('auth/passkey/register/complete/', PasskeyRegistrationCompleteView.as_view(), name='passkey-register-complete'),
    path('auth/passkey/authenticate/init/', PasskeyAuthenticationInitView.as_view(), name='passkey-auth-init'),
    path('auth/passkey/authenticate/complete/', PasskeyAuthenticationCompleteView.as_view(), name='passkey-auth-complete'),
    path('auth/passkey/credentials/', PasskeyCredentialListView.as_view(), name='passkey-credentials'),
    path('auth/passkey/credentials/<int:pk>/', PasskeyCredentialDeleteView.as_view(), name='passkey-credential-delete'),
]
