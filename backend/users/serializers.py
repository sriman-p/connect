from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import PasskeyCredential, PasskeyAuthenticationAttempt, PasskeyRegistrationSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Used for user profile display.
    """

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'avatar_url',
            'bio',
            'timezone',
            'is_verified',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Includes password validation and confirmation.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email',
            'full_name',
            'password',
            'password_confirm',
            'timezone',
        ]

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs

    def validate_email(self, value):
        """Validate email is unique and lowercase."""
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def create(self, validated_data):
        """Create new user with hashed password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user data.
    """

    def validate(self, attrs):
        """Add custom claims to token."""
        data = super().validate(attrs)

        # Add user data to response
        data['user'] = UserSerializer(self.user).data

        return data

    @classmethod
    def get_token(cls, user):
        """Add custom claims to token."""
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['is_verified'] = user.is_verified

        return token


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """

    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return attrs

    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    """

    token = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email exists."""
        value = value.lower()
        if not User.objects.filter(email=value).exists():
            # Don't reveal if email exists for security
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """

    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        return attrs


class PasskeyCredentialSerializer(serializers.ModelSerializer):
    """Serializer for passkey credentials."""

    class Meta:
        model = PasskeyCredential
        fields = [
            'id', 'credential_id', 'name', 'authenticator_type',
            'is_active', 'is_backup_eligible', 'is_backup_state',
            'device_name', 'usage_count', 'last_used_at',
            'created_at'
        ]
        read_only_fields = [
            'credential_id', 'usage_count', 'last_used_at', 'created_at'
        ]


class PasskeyRegistrationInitSerializer(serializers.Serializer):
    """Serializer for initiating passkey registration."""

    name = serializers.CharField(
        max_length=100,
        help_text='User-friendly name for the passkey (e.g., "iPhone Touch ID")'
    )


class PasskeyRegistrationCompleteSerializer(serializers.Serializer):
    """Serializer for completing passkey registration."""

    credential_id = serializers.CharField(max_length=500)
    public_key = serializers.CharField()
    challenge = serializers.CharField(max_length=500)
    attestation_data = serializers.JSONField(required=False)
    authenticator_type = serializers.ChoiceField(
        choices=['platform', 'cross_platform'],
        default='platform'
    )
    transports = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    device_name = serializers.CharField(max_length=200, required=False, allow_blank=True)


class PasskeyAuthenticationInitSerializer(serializers.Serializer):
    """Serializer for initiating passkey authentication."""

    email = serializers.EmailField(required=False)


class PasskeyAuthenticationCompleteSerializer(serializers.Serializer):
    """Serializer for completing passkey authentication."""

    credential_id = serializers.CharField(max_length=500)
    challenge = serializers.CharField(max_length=500)
    authenticator_data = serializers.CharField()
    client_data_json = serializers.CharField()
    signature = serializers.CharField()


class PasskeyAuthenticationAttemptSerializer(serializers.ModelSerializer):
    """Serializer for passkey authentication attempts."""

    class Meta:
        model = PasskeyAuthenticationAttempt
        fields = [
            'id', 'status', 'user_agent', 'ip_address',
            'country_code', 'city', 'attempted_at'
        ]
        read_only_fields = fields
