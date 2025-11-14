"""
Files Views
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import File, FileFolder, FileShare, FileVersion
from .serializers import (
    FileSerializer,
    FileListSerializer,
    FileUploadSerializer,
    FileFolderSerializer,
    FileShareSerializer,
    FileVersionSerializer,
)


class FileViewSet(viewsets.ModelViewSet):
    """ViewSet for files."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return FileListSerializer
        elif self.action == 'create':
            return FileUploadSerializer
        return FileSerializer

    def get_queryset(self):
        """Return files for user's workspaces."""
        user = self.request.user
        return File.objects.filter(
            workspace__members=user,
            is_archived=False
        ).select_related(
            'uploaded_by', 'workspace', 'project', 'folder'
        ).distinct().order_by('-uploaded_at')

    def perform_create(self, serializer):
        """Set uploader to current user."""
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Track file download."""
        file = self.get_object()
        file.download_count += 1
        file.save(update_fields=['download_count'])

        return Response({
            'message': 'Download tracked.',
            'url': file.file_url
        })

    @action(detail=True, methods=['post'])
    def star(self, request, pk=None):
        """Star/unstar a file."""
        file = self.get_object()
        file.is_starred = not file.is_starred
        file.save(update_fields=['is_starred'])

        return Response({
            'message': 'File starred.' if file.is_starred else 'File unstarred.',
            'is_starred': file.is_starred
        })

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a file."""
        file = self.get_object()
        file.is_archived = True
        file.save(update_fields=['is_archived'])

        return Response({
            'message': 'File archived.',
            'file': FileSerializer(file).data
        })

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a file with users."""
        file = self.get_object()
        user_ids = request.data.get('user_ids', [])
        permission_level = request.data.get('permission_level', 'view')

        shares = []
        for user_id in user_ids:
            share, created = FileShare.objects.get_or_create(
                file=file,
                user_id=user_id,
                defaults={
                    'shared_by': request.user,
                    'permission_level': permission_level
                }
            )
            shares.append(share)

        return Response({
            'message': f'File shared with {len(shares)} user(s).',
            'shares': FileShareSerializer(shares, many=True).data
        })

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get file versions."""
        file = self.get_object()
        versions = FileVersion.objects.filter(file=file).order_by('-version_number')

        return Response(FileVersionSerializer(versions, many=True).data)


class FileFolderViewSet(viewsets.ModelViewSet):
    """ViewSet for file folders."""

    serializer_class = FileFolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return folders for user's workspaces."""
        user = self.request.user
        return FileFolder.objects.filter(
            workspace__members=user
        ).select_related(
            'created_by', 'workspace', 'parent'
        ).distinct().order_by('name')

    def perform_create(self, serializer):
        """Set creator to current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def files(self, request, pk=None):
        """Get files in folder."""
        folder = self.get_object()
        files = File.objects.filter(
            folder=folder,
            is_archived=False
        ).select_related('uploaded_by')

        return Response(FileListSerializer(files, many=True).data)

    @action(detail=True, methods=['get'])
    def subfolders(self, request, pk=None):
        """Get subfolders."""
        folder = self.get_object()
        subfolders = FileFolder.objects.filter(parent=folder)

        return Response(FileFolderSerializer(subfolders, many=True).data)


class FileShareViewSet(viewsets.ModelViewSet):
    """ViewSet for file shares."""

    serializer_class = FileShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return file shares for user."""
        user = self.request.user
        return FileShare.objects.filter(
            file__workspace__members=user
        ).select_related(
            'file', 'user', 'shared_by'
        ).distinct()

    def perform_create(self, serializer):
        """Set sharer to current user."""
        serializer.save(shared_by=self.request.user)


class FileVersionViewSet(viewsets.ModelViewSet):
    """ViewSet for file versions."""

    serializer_class = FileVersionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return file versions for user."""
        user = self.request.user
        return FileVersion.objects.filter(
            file__workspace__members=user
        ).select_related('file', 'uploaded_by').distinct()

    def perform_create(self, serializer):
        """Set uploader to current user and increment version."""
        file = serializer.validated_data['file']
        latest_version = FileVersion.objects.filter(
            file=file
        ).order_by('-version_number').first()

        version_number = 1 if not latest_version else latest_version.version_number + 1

        serializer.save(
            uploaded_by=self.request.user,
            version_number=version_number
        )
