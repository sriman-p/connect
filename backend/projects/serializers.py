from rest_framework import serializers
from .models import Project, ProjectMember
from users.serializers import UserSerializer
from workspaces.serializers import WorkspaceSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """

    workspace_data = WorkspaceSerializer(source='workspace', read_only=True)
    lead_data = UserSerializer(source='lead', read_only=True)
    created_by_data = UserSerializer(source='created_by', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'workspace',
            'workspace_data',
            'name',
            'identifier',
            'description',
            'status',
            'start_date',
            'target_date',
            'completed_at',
            'lead',
            'lead_data',
            'created_by',
            'created_by_data',
            'color',
            'icon',
            'is_archived',
            'is_private',
            'issue_count',
            'completed_issue_count',
            'progress',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'completed_at',
            'issue_count',
            'completed_issue_count',
            'progress',
            'created_at',
            'updated_at',
        ]

    def validate_identifier(self, value):
        """Validate identifier is unique within workspace."""
        workspace = self.context.get('workspace')
        project_id = self.instance.id if self.instance else None

        if workspace and Project.objects.filter(
            workspace=workspace,
            identifier=value
        ).exclude(id=project_id).exists():
            raise serializers.ValidationError(
                'A project with this identifier already exists in this workspace.'
            )

        return value


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for ProjectMember model.
    """

    user_data = UserSerializer(source='user', read_only=True)
    project_data = ProjectSerializer(source='project', read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            'id',
            'project',
            'project_data',
            'user',
            'user_data',
            'added_at',
        ]
        read_only_fields = ['id', 'added_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating projects.
    """

    class Meta:
        model = Project
        fields = [
            'name',
            'identifier',
            'description',
            'status',
            'start_date',
            'target_date',
            'lead',
            'color',
            'icon',
            'is_private',
        ]

    def validate_identifier(self, value):
        """Validate identifier format."""
        if not value.isupper():
            raise serializers.ValidationError('Identifier must be uppercase.')
        if len(value) > 10:
            raise serializers.ValidationError('Identifier must be 10 characters or less.')
        return value
