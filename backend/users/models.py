from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError('Email address is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with email authentication and bitmap permissions.
    Memory-efficient design for enterprise-scale deployments.
    """

    # Core fields
    email = models.EmailField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='User email address (used for authentication)'
    )
    full_name = models.CharField(
        max_length=150,
        help_text='User full name'
    )

    # Profile fields
    avatar_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='URL to user avatar image'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        default='',
        help_text='User biography'
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text='User timezone'
    )

    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text='User account is active'
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Email address is verified'
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='User can access admin site'
    )

    # Global bitmap permissions (64 bits for system-level permissions)
    # Bit positions: 0-63 for different global permissions
    global_permissions = models.BigIntegerField(
        default=0,
        help_text='Bitmap for global system permissions (64 bits)'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Account creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last login timestamp'
    )

    # Manager
    objects = UserManager()

    # Authentication field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_verified', 'is_active']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def has_global_permission(self, permission_bit):
        """
        Check if user has a specific global permission using bitwise AND.

        Args:
            permission_bit (int): Bit position (0-63) to check

        Returns:
            bool: True if user has the permission
        """
        return bool(self.global_permissions & (1 << permission_bit))

    def grant_global_permission(self, permission_bit):
        """
        Grant a global permission to the user using bitwise OR.

        Args:
            permission_bit (int): Bit position (0-63) to grant
        """
        self.global_permissions |= (1 << permission_bit)
        self.save(update_fields=['global_permissions'])

    def revoke_global_permission(self, permission_bit):
        """
        Revoke a global permission from the user using bitwise AND NOT.

        Args:
            permission_bit (int): Bit position (0-63) to revoke
        """
        self.global_permissions &= ~(1 << permission_bit)
        self.save(update_fields=['global_permissions'])


class PasskeyCredential(models.Model):
    """
    WebAuthn/FIDO2 passkey credential for passwordless authentication.
    Stores public key credentials for biometric and hardware key authentication.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='passkey_credentials'
    )

    # WebAuthn credential identifier
    credential_id = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
        help_text='Unique credential identifier (base64url encoded)'
    )

    # Public key (stored for signature verification)
    public_key = models.TextField(
        help_text='Public key in PEM or COSE format'
    )

    # Credential metadata
    name = models.CharField(
        max_length=100,
        help_text='User-friendly name for the credential (e.g., "iPhone Touch ID")'
    )

    # Authenticator details
    aaguid = models.CharField(
        max_length=100,
        blank=True,
        help_text='Authenticator Attestation GUID'
    )

    authenticator_type = models.CharField(
        max_length=20,
        choices=[
            ('platform', 'Platform Authenticator'),  # Built-in (Touch ID, Face ID, Windows Hello)
            ('cross_platform', 'Cross-Platform'),     # External (YubiKey, security key)
        ],
        default='platform',
        help_text='Type of authenticator device'
    )

    # Attestation
    attestation_format = models.CharField(
        max_length=50,
        blank=True,
        help_text='Attestation statement format (packed, fido-u2f, android-key, etc.)'
    )

    attestation_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Full attestation statement and data'
    )

    # Signature counter (for detecting credential cloning)
    sign_count = models.BigIntegerField(
        default=0,
        help_text='Signature counter to detect cloned credentials'
    )

    # Transports (how the credential can be accessed)
    transports = models.JSONField(
        default=list,
        blank=True,
        help_text='List of supported transports (usb, nfc, ble, internal)'
    )

    # Usage tracking
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time this credential was used'
    )

    usage_count = models.IntegerField(
        default=0,
        help_text='Number of times this credential has been used'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Credential is active and can be used'
    )

    # Backup eligibility and state (for account recovery)
    is_backup_eligible = models.BooleanField(
        default=False,
        help_text='Credential can be backed up and synced'
    )

    is_backup_state = models.BooleanField(
        default=False,
        help_text='Credential is currently backed up'
    )

    # Device information
    device_name = models.CharField(
        max_length=200,
        blank=True,
        help_text='Device name where credential was created'
    )

    user_agent = models.TextField(
        blank=True,
        help_text='User agent when credential was created'
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address when credential was created'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Credential creation timestamp'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )

    class Meta:
        db_table = 'passkey_credentials'
        verbose_name = 'Passkey Credential'
        verbose_name_plural = 'Passkey Credentials'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['credential_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.name}"

    def increment_usage(self):
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])


class PasskeyAuthenticationAttempt(models.Model):
    """
    Track passkey authentication attempts for security monitoring.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='passkey_auth_attempts'
    )

    credential = models.ForeignKey(
        PasskeyCredential,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auth_attempts'
    )

    # Attempt details
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('invalid_signature', 'Invalid Signature'),
            ('credential_not_found', 'Credential Not Found'),
            ('user_not_found', 'User Not Found'),
            ('rate_limited', 'Rate Limited'),
        ],
        db_index=True
    )

    # Challenge used
    challenge = models.CharField(
        max_length=500,
        help_text='Challenge used for this authentication attempt'
    )

    # Request metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Location data (optional)
    country_code = models.CharField(max_length=2, blank=True)
    city = models.CharField(max_length=100, blank=True)

    # Error details (for failed attempts)
    error_message = models.TextField(blank=True)

    attempted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'passkey_auth_attempts'
        verbose_name = 'Passkey Authentication Attempt'
        verbose_name_plural = 'Passkey Authentication Attempts'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['user', 'attempted_at']),
            models.Index(fields=['status', 'attempted_at']),
            models.Index(fields=['ip_address', 'attempted_at']),
        ]

    def __str__(self):
        return f"{self.status} - {self.attempted_at}"


class PasskeyRegistrationSession(models.Model):
    """
    Temporary session for passkey registration (challenge storage).
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='passkey_registration_sessions'
    )

    # WebAuthn challenge
    challenge = models.CharField(
        max_length=500,
        unique=True,
        help_text='Random challenge for this registration session'
    )

    # Session metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Status
    is_completed = models.BooleanField(
        default=False,
        help_text='Registration was successfully completed'
    )

    is_expired = models.BooleanField(
        default=False,
        help_text='Session has expired'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text='Session expiration time (typically 5 minutes)'
    )

    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'passkey_registration_sessions'
        verbose_name = 'Passkey Registration Session'
        verbose_name_plural = 'Passkey Registration Sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_completed']),
            models.Index(fields=['challenge']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.created_at}"
