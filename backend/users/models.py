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
