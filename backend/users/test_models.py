"""
Tests for User model and permissions.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test User model functionality."""

    def test_create_user(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )

        assert user.email == 'test@example.com'
        assert user.full_name == 'Test User'
        assert user.is_active is True
        assert user.is_verified is False
        assert user.check_password('testpass123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            full_name='Admin User'
        )

        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.is_verified is True

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )

        assert str(user) == 'Test User (test@example.com)'

    def test_global_permissions(self):
        """Test bitmap global permissions."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )

        # Initially no permissions
        assert user.global_permissions == 0
        assert not user.has_global_permission(0)

        # Grant permission at bit 5
        user.grant_global_permission(5)
        assert user.has_global_permission(5)
        assert not user.has_global_permission(6)

        # Revoke permission
        user.revoke_global_permission(5)
        assert not user.has_global_permission(5)

    def test_email_normalization(self):
        """Test email is normalized (lowercase)."""
        user = User.objects.create_user(
            email='Test@Example.COM',
            password='testpass123',
            full_name='Test User'
        )

        assert user.email == 'test@example.com'
