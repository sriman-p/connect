"""
Documents API Views
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import (
    Document, DocumentEditor, DocumentVersion, DocumentComment,
    DocumentFolder, DocumentTemplate, DocumentSession, DocumentOperation
)
from .serializers import (
    DocumentSerializer, DocumentListSerializer, DocumentEditorSerializer,
    DocumentVersionSerializer, DocumentCommentSerializer,
    DocumentFolderSerializer, DocumentTemplateSerializer,
    DocumentSessionSerializer, DocumentOperationSerializer
)


class DocumentViewSet(viewsets.ModelViewSet):
    """Document CRUD operations."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workspace', 'project', 'doc_type', 'is_archived', 'permission_level']
    search_fields = ['title', 'plain_text']
    ordering_fields = ['created_at', 'updated_at', 'title', 'word_count']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer

    def get_queryset(self):
        """Filter documents by user access."""
        user = self.request.user
        return Document.objects.filter(
            Q(created_by=user) |
            Q(editors__user=user) |
            Q(permission_level__in=['workspace', 'public'])
        ).select_related(
            'created_by', 'last_edited_by', 'folder'
        ).prefetch_related(
            'editors'
        ).distinct()

    def perform_create(self, serializer):
        """Set created_by when creating document."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a document."""
        document = self.get_object()
        new_document = Document.objects.create(
            workspace=document.workspace,
            project=document.project,
            title=f"{document.title} (Copy)",
            doc_type=document.doc_type,
            content=document.content,
            plain_text=document.plain_text,
            created_by=request.user,
            permission_level=document.permission_level,
            folder=document.folder
        )
        serializer = self.get_serializer(new_document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a document."""
        document = self.get_object()
        document.is_archived = True
        document.save()
        return Response({'status': 'archived'})

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a document."""
        document = self.get_object()
        document.is_archived = False
        document.save()
        return Response({'status': 'unarchived'})

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a document."""
        from django.utils import timezone
        document = self.get_object()
        document.is_published = True
        document.published_at = timezone.now()
        document.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get document version history."""
        document = self.get_object()
        versions = document.versions.all()
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def active_sessions(self, request, pk=None):
        """Get active editing sessions."""
        document = self.get_object()
        sessions = document.active_sessions.filter(is_active=True)
        serializer = DocumentSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_editor(self, request, pk=None):
        """Add an editor to the document."""
        document = self.get_object()
        serializer = DocumentEditorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(document=document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_editor(self, request, pk=None):
        """Remove an editor from the document."""
        document = self.get_object()
        user_id = request.data.get('user_id')
        DocumentEditor.objects.filter(
            document=document,
            user_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentFolderViewSet(viewsets.ModelViewSet):
    """Document folder operations."""

    serializer_class = DocumentFolderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['workspace', 'parent_folder']
    search_fields = ['name', 'description']

    def get_queryset(self):
        """Filter folders by workspace."""
        return DocumentFolder.objects.filter(
            workspace__members=self.request.user
        ).select_related('created_by', 'parent_folder')

    def perform_create(self, serializer):
        """Set created_by when creating folder."""
        serializer.save(created_by=self.request.user)


class DocumentCommentViewSet(viewsets.ModelViewSet):
    """Document comment operations."""

    serializer_class = DocumentCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['document', 'is_resolved']

    def get_queryset(self):
        """Filter comments by document access."""
        user = self.request.user
        return DocumentComment.objects.filter(
            document__in=Document.objects.filter(
                Q(created_by=user) |
                Q(editors__user=user) |
                Q(permission_level__in=['workspace', 'public'])
            )
        ).select_related('author', 'resolved_by')

    def perform_create(self, serializer):
        """Set author when creating comment."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a comment."""
        from django.utils import timezone
        comment = self.get_object()
        comment.is_resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save()
        return Response({'status': 'resolved'})

    @action(detail=True, methods=['post'])
    def unresolve(self, request, pk=None):
        """Unresolve a comment."""
        comment = self.get_object()
        comment.is_resolved = False
        comment.resolved_by = None
        comment.resolved_at = None
        comment.save()
        return Response({'status': 'unresolved'})


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """Document template operations."""

    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['workspace', 'doc_type', 'is_public']
    search_fields = ['name', 'description']

    def get_queryset(self):
        """Filter templates by workspace or public."""
        user = self.request.user
        return DocumentTemplate.objects.filter(
            Q(workspace__members=user) |
            Q(is_public=True)
        ).select_related('created_by')

    def perform_create(self, serializer):
        """Set created_by when creating template."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Create a document from template."""
        template = self.get_object()
        document = Document.objects.create(
            workspace_id=request.data.get('workspace'),
            project_id=request.data.get('project'),
            title=request.data.get('title', template.name),
            doc_type=template.doc_type,
            content=template.content,
            created_by=request.user
        )
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
