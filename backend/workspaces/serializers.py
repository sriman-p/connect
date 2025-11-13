from rest_framework import serializers
from .models import Workspace, WorkspaceMember, WorkspacePermissions
from users.serializers import UserSerializer


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Serializer for Workspace model.
    """

    owner_data = UserSerializer(source='owner', read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'owner',
            'owner_data',
            'logo_url',
            'is_active',
            'member_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        """Get total member count."""
        return obj.members.filter(is_active=True).count()

    def validate_slug(self, value):
        """Validate slug is unique."""
        workspace_id = self.instance.id if self.instance else None
        if Workspace.objects.filter(slug=value).exclude(id=workspace_id).exists():
            raise serializers.ValidationError('A workspace with this slug already exists.')
        return value


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkspaceMember model.
    """

    user_data = UserSerializer(source='user', read_only=True)
    workspace_data = WorkspaceSerializer(source='workspace', read_only=True)
    permissions_list = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceMember
        fields = [
            'id',
            'workspace',
            'workspace_data',
            'user',
            'user_data',
            'role',
            'permissions',
            'permissions_list',
            'is_active',
            'joined_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'joined_at', 'updated_at']

    def get_permissions_list(self, obj):
        """Get list of permission names user has."""
        permissions = []
        permission_map = {
            WorkspacePermissions.VIEW_WORKSPACE: 'view_workspace',
            WorkspacePermissions.EDIT_WORKSPACE: 'edit_workspace',
            WorkspacePermissions.DELETE_WORKSPACE: 'delete_workspace',
            WorkspacePermissions.MANAGE_MEMBERS: 'manage_members',
            WorkspacePermissions.INVITE_MEMBERS: 'invite_members',
            WorkspacePermissions.REMOVE_MEMBERS: 'remove_members',
            WorkspacePermissions.VIEW_MEMBERS: 'view_members',
            WorkspacePermissions.MANAGE_SETTINGS: 'manage_settings',
            WorkspacePermissions.CREATE_PROJECT: 'create_project',
            WorkspacePermissions.EDIT_PROJECT: 'edit_project',
            WorkspacePermissions.DELETE_PROJECT: 'delete_project',
            WorkspacePermissions.ARCHIVE_PROJECT: 'archive_project',
            WorkspacePermissions.VIEW_PROJECT: 'view_project',
            WorkspacePermissions.MANAGE_PROJECT_MEMBERS: 'manage_project_members',
            WorkspacePermissions.CREATE_ISSUE: 'create_issue',
            WorkspacePermissions.EDIT_ISSUE: 'edit_issue',
            WorkspacePermissions.DELETE_ISSUE: 'delete_issue',
            WorkspacePermissions.ASSIGN_ISSUE: 'assign_issue',
            WorkspacePermissions.CHANGE_ISSUE_STATUS: 'change_issue_status',
            WorkspacePermissions.VIEW_ISSUE: 'view_issue',
            WorkspacePermissions.COMMENT_ISSUE: 'comment_issue',
            WorkspacePermissions.EDIT_ISSUE_COMMENTS: 'edit_issue_comments',
            WorkspacePermissions.CREATE_CHANNEL: 'create_channel',
            WorkspacePermissions.EDIT_CHANNEL: 'edit_channel',
            WorkspacePermissions.DELETE_CHANNEL: 'delete_channel',
            WorkspacePermissions.SEND_MESSAGE: 'send_message',
            WorkspacePermissions.DELETE_MESSAGE: 'delete_message',
            WorkspacePermissions.VIEW_CHANNEL: 'view_channel',
            WorkspacePermissions.MANAGE_INTEGRATIONS: 'manage_integrations',
            WorkspacePermissions.VIEW_ANALYTICS: 'view_analytics',
            WorkspacePermissions.EXPORT_DATA: 'export_data',
            WorkspacePermissions.MANAGE_BILLING: 'manage_billing',
            WorkspacePermissions.MANAGE_SECURITY: 'manage_security',
        }

        for bit, name in permission_map.items():
            if obj.has_permission(bit):
                permissions.append(name)

        return permissions


class WorkspaceMemberInviteSerializer(serializers.Serializer):
    """
    Serializer for inviting members to workspace.
    """

    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(
        choices=WorkspaceMember.ROLE_CHOICES,
        default=WorkspaceMember.MEMBER
    )

    def validate_email(self, value):
        """Validate email exists."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        value = value.lower()
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No user found with this email address.')
        return value


class WorkspaceMemberUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating workspace member role/permissions.
    """

    class Meta:
        model = WorkspaceMember
        fields = ['role', 'permissions', 'is_active']

    def update(self, instance, validated_data):
        """Update member and set role permissions if role changed."""
        role = validated_data.get('role')
        if role and role != instance.role:
            instance.role = role
            instance.set_role_permissions()

        for attr, value in validated_data.items():
            if attr != 'role':
                setattr(instance, attr, value)

        instance.save()
        return instance
