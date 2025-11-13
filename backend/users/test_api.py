"""
Tests for authentication API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthenticationAPI:
    """Test authentication endpoints."""

    def test_user_registration(self, api_client):
        """Test user registration endpoint."""
        url = reverse('users:register')
        data = {
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'timezone': 'UTC'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'newuser@example.com'

        # Check user was created in database
        user = User.objects.get(email='newuser@example.com')
        assert user.full_name == 'New User'

    def test_user_login(self, api_client, user):
        """Test user login endpoint."""
        url = reverse('users:login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == 'test@example.com'

    def test_user_login_wrong_password(self, api_client, user):
        """Test login with wrong password."""
        url = reverse('users:login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_profile(self, authenticated_client, user):
        """Test getting user profile."""
        url = reverse('users:profile')

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'test@example.com'
        assert response.data['full_name'] == 'Test User'

    def test_update_user_profile(self, authenticated_client, user):
        """Test updating user profile."""
        url = reverse('users:profile')
        data = {
            'full_name': 'Updated Name',
            'bio': 'Updated bio'
        }

        response = authenticated_client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Updated Name'
        assert response.data['bio'] == 'Updated bio'

        # Check database was updated
        user.refresh_from_db()
        assert user.full_name == 'Updated Name'

    def test_password_mismatch(self, api_client):
        """Test registration with password mismatch."""
        url = reverse('users:register')
        data = {
            'email': 'test2@example.com',
            'full_name': 'Test User 2',
            'password': 'password123',
            'password_confirm': 'differentpassword',
            'timezone': 'UTC'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_duplicate_email(self, api_client, user):
        """Test registration with existing email."""
        url = reverse('users:register')
        data = {
            'email': 'test@example.com',  # Already exists
            'full_name': 'Another User',
            'password': 'password123',
            'password_confirm': 'password123',
            'timezone': 'UTC'
        }

        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
