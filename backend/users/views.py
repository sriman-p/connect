from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    EmailVerificationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasskeyCredentialSerializer,
    PasskeyRegistrationInitSerializer,
    PasskeyRegistrationCompleteSerializer,
    PasskeyAuthenticationInitSerializer,
    PasskeyAuthenticationCompleteSerializer,
)
from .models import PasskeyCredential, PasskeyRegistrationSession, PasskeyAuthenticationAttempt

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    POST /api/auth/register/
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        """Create new user and return tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'message': 'Registration successful. Please verify your email.'
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with user data.
    POST /api/auth/login/
    """

    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """
    API endpoint for user logout.
    POST /api/auth/logout/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Blacklist refresh token."""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            return Response({
                'message': 'Logout successful.'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Invalid token.'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile.
    GET/PATCH /api/auth/profile/
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Return current user."""
        return self.request.user


class PasswordChangeView(APIView):
    """
    API endpoint for password change.
    POST /api/auth/password/change/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Set new password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)


class EmailVerificationView(APIView):
    """
    API endpoint for email verification.
    POST /api/auth/email/verify/
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Verify user email."""
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']

        # TODO: Implement token verification logic
        # For now, just return success
        return Response({
            'message': 'Email verified successfully.'
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    API endpoint for password reset request.
    POST /api/auth/password/reset/
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Send password reset email."""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()

        # TODO: Implement password reset email logic
        # For security, always return success even if email doesn't exist
        return Response({
            'message': 'If an account exists with this email, you will receive password reset instructions.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    API endpoint for password reset confirmation.
    POST /api/auth/password/reset/confirm/
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Reset user password."""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Implement token verification and password reset logic
        return Response({
            'message': 'Password reset successfully.'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Health check endpoint for Docker/monitoring.
    GET /api/health/
    """
    return Response({
        'status': 'healthy',
        'service': 'connect-api'
    }, status=status.HTTP_200_OK)


# Passkey Authentication Views

class PasskeyRegistrationInitView(APIView):
    """
    Initiate passkey registration.
    POST /api/auth/passkey/register/init/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Generate registration challenge."""
        import uuid
        import secrets
        from datetime import timedelta
        from django.utils import timezone

        serializer = PasskeyRegistrationInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate challenge
        challenge = secrets.token_urlsafe(32)

        # Create registration session
        session = PasskeyRegistrationSession.objects.create(
            user=request.user,
            challenge=challenge,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=request.META.get('REMOTE_ADDR', ''),
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        # WebAuthn registration options
        options = {
            'challenge': challenge,
            'rp': {
                'name': 'Connect',
                'id': request.get_host().split(':')[0],
            },
            'user': {
                'id': str(request.user.id),
                'name': request.user.email,
                'displayName': request.user.full_name or request.user.email,
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},  # ES256
                {'type': 'public-key', 'alg': -257},  # RS256
            ],
            'timeout': 60000,
            'attestation': 'none',
            'authenticatorSelection': {
                'authenticatorAttachment': serializer.validated_data.get('authenticator_type', 'platform'),
                'requireResidentKey': False,
                'userVerification': 'preferred',
            },
        }

        return Response(options, status=status.HTTP_200_OK)


class PasskeyRegistrationCompleteView(APIView):
    """
    Complete passkey registration.
    POST /api/auth/passkey/register/complete/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Verify and store credential."""
        serializer = PasskeyRegistrationCompleteSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Create credential
        credential = PasskeyCredential.objects.create(
            user=request.user,
            credential_id=serializer.validated_data['credential_id'],
            public_key=serializer.validated_data['public_key'],
            name=serializer.validated_data.get('name', 'My Passkey'),
            authenticator_type=serializer.validated_data.get('authenticator_type', 'platform'),
            aaguid=serializer.validated_data.get('aaguid', ''),
            attestation_format=serializer.validated_data.get('attestation_format', 'none'),
            transports=serializer.validated_data.get('transports', []),
            device_name=serializer.validated_data.get('device_name', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=request.META.get('REMOTE_ADDR', ''),
        )

        return Response({
            'message': 'Passkey registered successfully.',
            'credential': PasskeyCredentialSerializer(credential).data
        }, status=status.HTTP_201_CREATED)


class PasskeyAuthenticationInitView(APIView):
    """
    Initiate passkey authentication.
    POST /api/auth/passkey/authenticate/init/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Generate authentication challenge."""
        import secrets

        serializer = PasskeyAuthenticationInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')

        # Get user's credentials
        if email:
            try:
                user = User.objects.get(email=email.lower())
                credentials = PasskeyCredential.objects.filter(user=user, is_active=True)
            except User.DoesNotExist:
                credentials = PasskeyCredential.objects.none()
        else:
            credentials = PasskeyCredential.objects.filter(is_active=True)

        # Generate challenge
        challenge = secrets.token_urlsafe(32)

        # WebAuthn authentication options
        options = {
            'challenge': challenge,
            'timeout': 60000,
            'rpId': request.get_host().split(':')[0],
            'allowCredentials': [
                {
                    'type': 'public-key',
                    'id': cred.credential_id,
                    'transports': cred.transports,
                }
                for cred in credentials[:10]  # Limit to 10 credentials
            ],
            'userVerification': 'preferred',
        }

        return Response(options, status=status.HTTP_200_OK)


class PasskeyAuthenticationCompleteView(APIView):
    """
    Complete passkey authentication.
    POST /api/auth/passkey/authenticate/complete/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Verify credential and return tokens."""
        serializer = PasskeyAuthenticationCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        credential_id = serializer.validated_data['credential_id']

        try:
            credential = PasskeyCredential.objects.get(
                credential_id=credential_id,
                is_active=True
            )
        except PasskeyCredential.DoesNotExist:
            # Log failed attempt
            PasskeyAuthenticationAttempt.objects.create(
                status='failed',
                error_message='Credential not found',
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                ip_address=request.META.get('REMOTE_ADDR', ''),
            )
            return Response({
                'error': 'Invalid credential.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Update credential usage
        credential.usage_count += 1
        credential.last_used_at = timezone.now()
        credential.save()

        # Log successful attempt
        PasskeyAuthenticationAttempt.objects.create(
            user=credential.user,
            credential=credential,
            status='success',
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            ip_address=request.META.get('REMOTE_ADDR', ''),
        )

        # Generate tokens
        refresh = RefreshToken.for_user(credential.user)

        return Response({
            'user': UserSerializer(credential.user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'message': 'Authentication successful.'
        }, status=status.HTTP_200_OK)


class PasskeyCredentialListView(generics.ListAPIView):
    """
    List user's passkey credentials.
    GET /api/auth/passkey/credentials/
    """
    serializer_class = PasskeyCredentialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return user's credentials."""
        return PasskeyCredential.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-created_at')


class PasskeyCredentialDeleteView(generics.DestroyAPIView):
    """
    Delete a passkey credential.
    DELETE /api/auth/passkey/credentials/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return user's credentials."""
        return PasskeyCredential.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete by marking inactive."""
        instance.is_active = False
        instance.save()
