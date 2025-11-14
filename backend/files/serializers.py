"""
Files Serializers
"""

from rest_framework import serializers
from .models import File, FileFolder, FileShare, FileVersion
from users.serializers import UserSerializer


class FileVersionSerializer(serializers.ModelSerializer):
    """Serializer for file versions."""

    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = FileVersion
        fields = [
            'id', 'file', 'version_number', 'file_url',
            'file_size', 'comment', 'uploaded_by', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']


class FileShareSerializer(serializers.ModelSerializer):
    """Serializer for file shares."""

    user = UserSerializer(read_only=True)
    shared_by = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FileShare
        fields = [
            'id', 'file', 'user', 'user_id', 'shared_by',
            'permission_level', 'shared_at', 'expires_at'
        ]
        read_only_fields = ['id', 'shared_by', 'shared_at']


class FileFolderSerializer(serializers.ModelSerializer):
    """Serializer for file folders."""

    created_by = UserSerializer(read_only=True)
    file_count = serializers.SerializerMethodField()
    subfolder_count = serializers.SerializerMethodField()

    class Meta:
        model = FileFolder
        fields = [
            'id', 'workspace', 'parent', 'name', 'description',
            'color', 'created_by', 'is_public', 'file_count',
            'subfolder_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_file_count(self, obj):
        """Get number of files in folder."""
        return obj.files.count()

    def get_subfolder_count(self, obj):
        """Get number of subfolders."""
        return FileFolder.objects.filter(parent=obj).count()


class FileSerializer(serializers.ModelSerializer):
    """Full serializer for files."""

    uploaded_by = UserSerializer(read_only=True)
    shared_with_data = FileShareSerializer(
        source='fileshare_set',
        many=True,
        read_only=True
    )
    versions = FileVersionSerializer(many=True, read_only=True)
    folder_data = FileFolderSerializer(source='folder', read_only=True)

    class Meta:
        model = File
        fields = [
            'id', 'workspace', 'project', 'folder', 'folder_data',
            'name', 'file_type', 'mime_type', 'file_size',
            'file_url', 'file_path', 'thumbnail_url', 'preview_url',
            'uploaded_by', 'shared_with_data', 'is_public',
            'is_archived', 'is_starred', 'is_scanned', 'scan_status',
            'description', 'tags', 'versions', 'download_count',
            'uploaded_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'uploaded_by', 'file_size', 'mime_type',
            'download_count', 'uploaded_at', 'updated_at'
        ]


class FileListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for file lists."""

    uploaded_by = UserSerializer(read_only=True)
    folder_name = serializers.CharField(source='folder.name', read_only=True)

    class Meta:
        model = File
        fields = [
            'id', 'name', 'file_type', 'file_size', 'file_url',
            'thumbnail_url', 'uploaded_by', 'folder_name',
            'is_public', 'is_starred', 'uploaded_at'
        ]


class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file uploads."""

    class Meta:
        model = File
        fields = [
            'workspace', 'project', 'folder', 'name',
            'file_type', 'mime_type', 'file_size',
            'file_url', 'file_path', 'thumbnail_url',
            'description', 'tags', 'is_public'
        ]

    def create(self, validated_data):
        """Create file with scan status."""
        file = File.objects.create(
            **validated_data,
            scan_status='pending'
        )
        return file
