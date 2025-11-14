"""
Documents API Serializers
"""

from rest_framework import serializers
from .models import (
    Document, DocumentEditor, DocumentVersion, DocumentComment,
    DocumentFolder, DocumentTemplate, DocumentSession, DocumentOperation
)
from users.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization."""

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'avatar_url']
        read_only_fields = fields


class DocumentEditorSerializer(serializers.ModelSerializer):
    """Document editor permissions serializer."""

    user = UserBasicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = DocumentEditor
        fields = [
            'id', 'user', 'user_id', 'role',
            'added_at', 'last_viewed_at'
        ]
        read_only_fields = ['added_at', 'last_viewed_at']


class DocumentFolderSerializer(serializers.ModelSerializer):
    """Document folder serializer."""

    created_by = UserBasicSerializer(read_only=True)
    subfolders = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentFolder
        fields = [
            'id', 'workspace', 'name', 'description',
            'parent_folder', 'created_by', 'color',
            'created_at', 'updated_at', 'subfolders',
            'document_count'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_subfolders(self, obj):
        """Get subfolders recursively."""
        subfolders = obj.subfolders.all()
        return DocumentFolderSerializer(subfolders, many=True).data

    def get_document_count(self, obj):
        """Get count of documents in folder."""
        return obj.documents.count()


class DocumentSerializer(serializers.ModelSerializer):
    """Main document serializer."""

    created_by = UserBasicSerializer(read_only=True)
    last_edited_by = UserBasicSerializer(read_only=True)
    folder_data = DocumentFolderSerializer(source='folder', read_only=True)
    editors_data = DocumentEditorSerializer(
        source='documenteditor_set',
        many=True,
        read_only=True
    )
    active_sessions_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'workspace', 'project', 'title', 'slug',
            'doc_type', 'content', 'plain_text',
            'created_by', 'last_edited_by',
            'is_template', 'is_archived', 'is_published',
            'permission_level', 'version',
            'folder', 'folder_data', 'word_count', 'view_count',
            'created_at', 'updated_at', 'published_at',
            'editors_data', 'active_sessions_count'
        ]
        read_only_fields = [
            'slug', 'created_by', 'last_edited_by',
            'word_count', 'view_count', 'version',
            'created_at', 'updated_at'
        ]

    def get_active_sessions_count(self, obj):
        """Get count of active editing sessions."""
        return obj.active_sessions.filter(is_active=True).count()


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight document serializer for lists."""

    created_by = UserBasicSerializer(read_only=True)
    last_edited_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'slug', 'doc_type',
            'created_by', 'last_edited_by',
            'is_archived', 'permission_level',
            'word_count', 'view_count',
            'updated_at', 'created_at'
        ]
        read_only_fields = fields


class DocumentVersionSerializer(serializers.ModelSerializer):
    """Document version history serializer."""

    created_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'document', 'version_number',
            'content', 'changes_summary',
            'created_by', 'created_at'
        ]
        read_only_fields = ['created_at']


class DocumentCommentSerializer(serializers.ModelSerializer):
    """Document comment serializer."""

    author = UserBasicSerializer(read_only=True)
    resolved_by_user = UserBasicSerializer(source='resolved_by', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = DocumentComment
        fields = [
            'id', 'document', 'author', 'content',
            'position', 'parent_comment',
            'is_resolved', 'resolved_by_user', 'resolved_at',
            'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        """Get comment replies."""
        if obj.parent_comment is None:
            replies = obj.replies.all()
            return DocumentCommentSerializer(replies, many=True).data
        return []


class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Document template serializer."""

    created_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'workspace', 'name', 'description',
            'doc_type', 'content', 'thumbnail_url',
            'is_public', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_at']


class DocumentSessionSerializer(serializers.ModelSerializer):
    """Active document session serializer."""

    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = DocumentSession
        fields = [
            'id', 'document', 'user', 'session_id',
            'is_active', 'cursor_position', 'selection_range',
            'user_color', 'joined_at', 'last_activity_at'
        ]
        read_only_fields = [
            'session_id', 'user_color',
            'joined_at', 'last_activity_at'
        ]


class DocumentOperationSerializer(serializers.ModelSerializer):
    """Document operation serializer."""

    session = DocumentSessionSerializer(read_only=True)

    class Meta:
        model = DocumentOperation
        fields = [
            'id', 'document', 'session',
            'operation_type', 'operation_data',
            'base_version', 'sequence_number',
            'is_acknowledged', 'acknowledged_at',
            'created_at'
        ]
        read_only_fields = ['created_at']
