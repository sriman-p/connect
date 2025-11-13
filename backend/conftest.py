"""
Pytest configuration and fixtures for Connect backend tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a test user."""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        full_name='Test User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def workspace(db, user):
    """Create and return a test workspace."""
    from workspaces.models import Workspace, WorkspaceMember

    workspace = Workspace.objects.create(
        name='Test Workspace',
        slug='test-workspace',
        owner=user
    )

    # Add owner as member with full permissions
    WorkspaceMember.objects.create(
        workspace=workspace,
        user=user,
        role=WorkspaceMember.OWNER,
        permissions=(1 << 64) - 1,  # All permissions
        is_active=True
    )

    return workspace


@pytest.fixture
def project(db, workspace, user):
    """Create and return a test project."""
    from projects.models import Project, ProjectMember

    project = Project.objects.create(
        workspace=workspace,
        name='Test Project',
        identifier='TEST',
        created_by=user
    )

    # Add creator as member
    ProjectMember.objects.create(
        project=project,
        user=user
    )

    return project


@pytest.fixture
def issue(db, workspace, project, user):
    """Create and return a test issue."""
    from issues.models import Issue

    return Issue.objects.create(
        workspace=workspace,
        project=project,
        title='Test Issue',
        description='Test description',
        reporter=user,
        status=Issue.TODO
    )


@pytest.fixture
def label(db, workspace):
    """Create and return a test label."""
    from issues.models import Label

    return Label.objects.create(
        workspace=workspace,
        name='Bug',
        color='#FF0000'
    )
