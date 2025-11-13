from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Label, Issue, IssueComment, IssueAttachment
from .serializers import (
    LabelSerializer,
    IssueSerializer,
    IssueCreateSerializer,
    IssueUpdateSerializer,
    IssueCommentSerializer,
    IssueAttachmentSerializer,
)

User = get_user_model()


class LabelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Label CRUD operations.
    Endpoints:
    - GET /api/labels/ - List labels
    - POST /api/labels/ - Create label
    - GET /api/labels/{id}/ - Get label details
    - PATCH /api/labels/{id}/ - Update label
    - DELETE /api/labels/{id}/ - Delete label
    """

    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return labels for workspaces user has access to."""
        user = self.request.user
        workspace_id = self.request.query_params.get('workspace')

        queryset = Label.objects.filter(
            workspace__members__user=user,
            workspace__is_active=True
        ).distinct()

        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Issue CRUD operations with Kanban support.
    Endpoints:
    - GET /api/issues/ - List issues
    - POST /api/issues/ - Create issue
    - GET /api/issues/{id}/ - Get issue details
    - PATCH /api/issues/{id}/ - Update issue
    - DELETE /api/issues/{id}/ - Delete issue
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'identifier']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'sort_order']
    ordering = ['sort_order', '-created_at']

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == 'create':
            return IssueCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IssueUpdateSerializer
        return IssueSerializer

    def get_queryset(self):
        """Return issues user has access to with filtering."""
        user = self.request.user

        # Base queryset
        queryset = Issue.objects.filter(
            workspace__members__user=user,
            workspace__is_active=True
        ).distinct().select_related(
            'workspace',
            'project',
            'assignee',
            'reporter',
            'parent'
        ).prefetch_related('labels', 'comments', 'attachments')

        # Filter by workspace
        workspace_id = self.request.query_params.get('workspace')
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        # Filter by project
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by assignee
        assignee_id = self.request.query_params.get('assignee')
        if assignee_id:
            if assignee_id == 'me':
                queryset = queryset.filter(assignee=user)
            elif assignee_id == 'unassigned':
                queryset = queryset.filter(assignee__isnull=True)
            else:
                queryset = queryset.filter(assignee_id=assignee_id)

        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by labels
        labels = self.request.query_params.get('labels')
        if labels:
            label_ids = labels.split(',')
            queryset = queryset.filter(labels__id__in=label_ids)

        # Filter by parent (sub-issues)
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        return queryset

    def perform_create(self, serializer):
        """Create issue with auto-generated identifier."""
        project_id = self.request.data.get('project')

        # Validate project access
        from projects.models import Project
        from workspaces.models import WorkspaceMember

        try:
            project = Project.objects.get(id=project_id)
            WorkspaceMember.objects.get(
                workspace=project.workspace,
                user=self.request.user,
                is_active=True
            )
        except (Project.DoesNotExist, WorkspaceMember.DoesNotExist):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have access to this project.')

        issue = serializer.save(
            workspace=project.workspace,
            reporter=self.request.user
        )

        # Update project metrics
        project.update_metrics()

    def perform_update(self, serializer):
        """Update issue and handle status changes."""
        old_status = self.get_object().status
        issue = serializer.save()
        new_status = issue.status

        # Track status changes
        if old_status != new_status:
            from django.utils import timezone

            if new_status == Issue.IN_PROGRESS and not issue.started_at:
                issue.started_at = timezone.now()
            elif new_status == Issue.DONE and not issue.completed_at:
                issue.completed_at = timezone.now()
            elif new_status == Issue.CANCELLED and not issue.cancelled_at:
                issue.cancelled_at = timezone.now()

            issue.save(update_fields=['started_at', 'completed_at', 'cancelled_at'])

        # Update project metrics
        issue.project.update_metrics()

    def destroy(self, request, *args, **kwargs):
        """Delete issue and update project metrics."""
        instance = self.get_object()
        project = instance.project

        instance.delete()

        # Update project metrics
        project.update_metrics()

        return Response({
            'message': 'Issue deleted successfully.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Get all comments for an issue.
        GET /api/issues/{id}/comments/
        """
        issue = self.get_object()
        comments = issue.comments.all().select_related('author')
        serializer = IssueCommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Add a comment to issue.
        POST /api/issues/{id}/add_comment/
        Body: {"content": "Comment text"}
        """
        issue = self.get_object()
        content = request.data.get('content')

        if not content:
            return Response({
                'error': 'Content is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = IssueComment.objects.create(
            issue=issue,
            author=request.user,
            content=content
        )

        return Response({
            'message': 'Comment added successfully.',
            'comment': IssueCommentSerializer(comment).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign issue to a user.
        POST /api/issues/{id}/assign/
        Body: {"user_id": 123}
        """
        issue = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            # Unassign
            issue.assignee = None
            issue.save()
            return Response({
                'message': 'Issue unassigned.',
                'issue': IssueSerializer(issue).data
            })

        try:
            user = User.objects.get(id=user_id)
            issue.assignee = user
            issue.save()

            return Response({
                'message': f'Issue assigned to {user.email}.',
                'issue': IssueSerializer(issue).data
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """
        Move issue to different status (Kanban column).
        POST /api/issues/{id}/move/
        Body: {"status": "in_progress", "sort_order": 5}
        """
        issue = self.get_object()
        new_status = request.data.get('status')
        sort_order = request.data.get('sort_order')

        if not new_status:
            return Response({
                'error': 'Status is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate status
        valid_statuses = [choice[0] for choice in Issue.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update status
        old_status = issue.status
        issue.status = new_status

        if sort_order is not None:
            issue.sort_order = sort_order

        # Track status changes
        from django.utils import timezone
        if new_status == Issue.IN_PROGRESS and not issue.started_at:
            issue.started_at = timezone.now()
        elif new_status == Issue.DONE and not issue.completed_at:
            issue.completed_at = timezone.now()
        elif new_status == Issue.CANCELLED and not issue.cancelled_at:
            issue.cancelled_at = timezone.now()

        issue.save()

        # Update project metrics
        issue.project.update_metrics()

        return Response({
            'message': f'Issue moved from {old_status} to {new_status}.',
            'issue': IssueSerializer(issue).data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """
        Get issues organized by Kanban columns.
        GET /api/issues/kanban/?project=123
        """
        project_id = request.query_params.get('project')
        if not project_id:
            return Response({
                'error': 'Project ID is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all issues for project
        issues = self.get_queryset().filter(project_id=project_id)

        # Organize by status
        kanban_board = {
            'backlog': [],
            'todo': [],
            'in_progress': [],
            'in_review': [],
            'done': [],
            'cancelled': [],
        }

        for issue in issues:
            serialized = IssueSerializer(issue).data
            kanban_board[issue.status].append(serialized)

        return Response(kanban_board)


class IssueCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for IssueComment management.
    Endpoints:
    - GET /api/issue-comments/ - List comments
    - POST /api/issue-comments/ - Create comment
    - PATCH /api/issue-comments/{id}/ - Update comment
    - DELETE /api/issue-comments/{id}/ - Delete comment
    """

    serializer_class = IssueCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return comments user can access."""
        user = self.request.user
        return IssueComment.objects.filter(
            issue__workspace__members__user=user
        ).distinct().select_related('issue', 'author')

    def perform_create(self, serializer):
        """Create comment."""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Mark comment as edited."""
        serializer.save(is_edited=True)
