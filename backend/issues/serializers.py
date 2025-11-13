from rest_framework import serializers
from .models import Label, Issue, IssueComment, IssueAttachment
from users.serializers import UserSerializer
from projects.serializers import ProjectSerializer


class LabelSerializer(serializers.ModelSerializer):
    """Serializer for Label model."""

    class Meta:
        model = Label
        fields = ['id', 'workspace', 'name', 'description', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


class IssueAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for IssueAttachment model."""

    uploaded_by_data = UserSerializer(source='uploaded_by', read_only=True)

    class Meta:
        model = IssueAttachment
        fields = [
            'id',
            'issue',
            'uploaded_by',
            'uploaded_by_data',
            'file_name',
            'file_url',
            'file_size',
            'file_type',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']


class IssueCommentSerializer(serializers.ModelSerializer):
    """Serializer for IssueComment model."""

    author_data = UserSerializer(source='author', read_only=True)

    class Meta:
        model = IssueComment
        fields = [
            'id',
            'issue',
            'author',
            'author_data',
            'content',
            'is_edited',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'author', 'is_edited', 'created_at', 'updated_at']


class IssueSerializer(serializers.ModelSerializer):
    """Serializer for Issue model."""

    workspace_data = serializers.SerializerMethodField()
    project_data = ProjectSerializer(source='project', read_only=True)
    assignee_data = UserSerializer(source='assignee', read_only=True)
    reporter_data = UserSerializer(source='reporter', read_only=True)
    labels_data = LabelSerializer(source='labels', many=True, read_only=True)
    parent_data = serializers.SerializerMethodField()
    comments = IssueCommentSerializer(many=True, read_only=True)
    attachments = IssueAttachmentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    sub_issue_count = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id',
            'workspace',
            'workspace_data',
            'project',
            'project_data',
            'identifier',
            'title',
            'description',
            'issue_type',
            'priority',
            'status',
            'assignee',
            'assignee_data',
            'reporter',
            'reporter_data',
            'labels',
            'labels_data',
            'parent',
            'parent_data',
            'sort_order',
            'estimate',
            'due_date',
            'started_at',
            'completed_at',
            'cancelled_at',
            'created_at',
            'updated_at',
            'comments',
            'attachments',
            'comment_count',
            'sub_issue_count',
        ]
        read_only_fields = [
            'id',
            'identifier',
            'reporter',
            'started_at',
            'completed_at',
            'cancelled_at',
            'created_at',
            'updated_at',
        ]

    def get_workspace_data(self, obj):
        """Get workspace data from project."""
        from workspaces.serializers import WorkspaceSerializer
        return WorkspaceSerializer(obj.workspace).data if obj.workspace else None

    def get_parent_data(self, obj):
        """Get parent issue data (simplified to avoid recursion)."""
        if obj.parent:
            return {
                'id': obj.parent.id,
                'identifier': obj.parent.identifier,
                'title': obj.parent.title,
                'status': obj.parent.status,
            }
        return None

    def get_comment_count(self, obj):
        """Get total comment count."""
        return obj.comments.count()

    def get_sub_issue_count(self, obj):
        """Get sub-issue count."""
        return obj.sub_issues.count()


class IssueCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating issues."""

    class Meta:
        model = Issue
        fields = [
            'project',
            'title',
            'description',
            'issue_type',
            'priority',
            'status',
            'assignee',
            'labels',
            'parent',
            'estimate',
            'due_date',
        ]


class IssueUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating issues."""

    class Meta:
        model = Issue
        fields = [
            'title',
            'description',
            'issue_type',
            'priority',
            'status',
            'assignee',
            'labels',
            'sort_order',
            'estimate',
            'due_date',
        ]
