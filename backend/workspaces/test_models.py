"""
Tests for Workspace models and bitmap permissions.
"""

import pytest
from workspaces.models import Workspace, WorkspaceMember, WorkspacePermissions


@pytest.mark.django_db
class TestWorkspaceModel:
    """Test Workspace model functionality."""

    def test_create_workspace(self, user):
        """Test creating a workspace."""
        workspace = Workspace.objects.create(
            name='Test Workspace',
            slug='test-workspace',
            owner=user
        )

        assert workspace.name == 'Test Workspace'
        assert workspace.slug == 'test-workspace'
        assert workspace.owner == user
        assert workspace.is_active is True

    def test_workspace_string_representation(self, workspace):
        """Test workspace string representation."""
        assert str(workspace) == 'Test Workspace'


@pytest.mark.django_db
class TestWorkspaceMemberModel:
    """Test WorkspaceMember model and bitmap permissions."""

    def test_create_member(self, workspace, user):
        """Test creating a workspace member."""
        member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=user
        ).first()

        assert member is not None
        assert member.role == WorkspaceMember.OWNER
        assert member.is_active is True

    def test_bitmap_permissions(self, workspace, user):
        """Test bitmap permission system."""
        member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=user
        ).first()

        # Owner should have all permissions
        assert member.has_permission(WorkspacePermissions.VIEW_WORKSPACE)
        assert member.has_permission(WorkspacePermissions.EDIT_WORKSPACE)
        assert member.has_permission(WorkspacePermissions.CREATE_PROJECT)
        assert member.has_permission(WorkspacePermissions.MANAGE_BILLING)

    def test_grant_and_revoke_permission(self, workspace):
        """Test granting and revoking individual permissions."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Create a new user with no permissions
        new_user = User.objects.create_user(
            email='member@example.com',
            password='pass123',
            full_name='Member User'
        )

        member = WorkspaceMember.objects.create(
            workspace=workspace,
            user=new_user,
            role=WorkspaceMember.GUEST,
            permissions=0  # No permissions
        )

        # Grant VIEW_WORKSPACE permission
        assert not member.has_permission(WorkspacePermissions.VIEW_WORKSPACE)
        member.grant_permission(WorkspacePermissions.VIEW_WORKSPACE)
        assert member.has_permission(WorkspacePermissions.VIEW_WORKSPACE)

        # Should not have other permissions
        assert not member.has_permission(WorkspacePermissions.CREATE_PROJECT)

        # Revoke permission
        member.revoke_permission(WorkspacePermissions.VIEW_WORKSPACE)
        assert not member.has_permission(WorkspacePermissions.VIEW_WORKSPACE)

    def test_set_role_permissions(self, workspace):
        """Test automatic permission assignment by role."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.create_user(
            email='test2@example.com',
            password='pass123',
            full_name='Test User 2'
        )

        # Create member role
        member = WorkspaceMember.objects.create(
            workspace=workspace,
            user=user,
            role=WorkspaceMember.MEMBER
        )
        member.set_role_permissions()

        # Member should have basic permissions (bits 0-31)
        assert member.has_permission(WorkspacePermissions.VIEW_WORKSPACE)
        assert member.has_permission(WorkspacePermissions.CREATE_ISSUE)

        # But not advanced permissions (bits 56-63)
        assert not member.has_permission(WorkspacePermissions.MANAGE_BILLING)

        # Change to admin
        member.role = WorkspaceMember.ADMIN
        member.set_role_permissions()

        # Admin should have most permissions
        assert member.has_permission(WorkspacePermissions.VIEW_WORKSPACE)
        assert member.has_permission(WorkspacePermissions.CREATE_ISSUE)
        assert member.has_permission(WorkspacePermissions.VIEW_ANALYTICS)

    def test_member_string_representation(self, workspace, user):
        """Test member string representation."""
        member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=user
        ).first()

        assert str(member) == 'test@example.com in Test Workspace'
