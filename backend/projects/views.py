from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Project, ProjectMember
from .serializers import (
    ProjectSerializer,
    ProjectMemberSerializer,
    ProjectCreateSerializer,
)

User = get_user_model()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations.
    Endpoints:
    - GET /api/projects/ - List projects
    - POST /api/projects/ - Create project
    - GET /api/projects/{id}/ - Get project details
    - PATCH /api/projects/{id}/ - Update project
    - DELETE /api/projects/{id}/ - Archive project
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializer for create."""
        if self.action == 'create':
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_queryset(self):
        """Return projects user has access to."""
        user = self.request.user
        workspace_id = self.request.query_params.get('workspace')

        queryset = Project.objects.filter(
            workspace__members__user=user,
            workspace__is_active=True,
            is_archived=False
        ).distinct().select_related('workspace', 'lead', 'created_by')

        # Filter by workspace
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset

    def get_serializer_context(self):
        """Add workspace to context for validation."""
        context = super().get_serializer_context()
        workspace_id = self.request.data.get('workspace')
        if workspace_id:
            from workspaces.models import Workspace
            try:
                context['workspace'] = Workspace.objects.get(id=workspace_id)
            except Workspace.DoesNotExist:
                pass
        return context

    def perform_create(self, serializer):
        """Create project and add creator as member."""
        workspace_id = self.request.data.get('workspace')

        # Validate workspace access
        from workspaces.models import Workspace, WorkspaceMember
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            WorkspaceMember.objects.get(
                workspace=workspace,
                user=self.request.user,
                is_active=True
            )
        except (Workspace.DoesNotExist, WorkspaceMember.DoesNotExist):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have access to this workspace.')

        project = serializer.save(
            workspace=workspace,
            created_by=self.request.user
        )

        # Add creator as project member
        ProjectMember.objects.create(
            project=project,
            user=self.request.user
        )

    def destroy(self, request, *args, **kwargs):
        """Archive project instead of deleting."""
        instance = self.get_object()
        instance.is_archived = True
        instance.save()

        return Response({
            'message': 'Project archived successfully.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        Get all members of a project.
        GET /api/projects/{id}/members/
        """
        project = self.get_object()
        members = ProjectMember.objects.filter(
            project=project
        ).select_related('user')

        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """
        Add a member to project.
        POST /api/projects/{id}/add_member/
        Body: {"user_id": 123}
        """
        project = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({
                'error': 'user_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if already a member
        if ProjectMember.objects.filter(project=project, user=user).exists():
            return Response({
                'error': 'User is already a member of this project.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create membership
        member = ProjectMember.objects.create(
            project=project,
            user=user
        )

        return Response({
            'message': f'{user.email} added to project.',
            'member': ProjectMemberSerializer(member).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """
        Remove a member from project.
        POST /api/projects/{id}/remove_member/
        Body: {"user_id": 123}
        """
        project = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({
                'error': 'user_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            member = ProjectMember.objects.get(project=project, user_id=user_id)
            member.delete()

            return Response({
                'message': 'Member removed from project.'
            }, status=status.HTTP_200_OK)
        except ProjectMember.DoesNotExist:
            return Response({
                'error': 'Member not found in project.'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_metrics(self, request, pk=None):
        """
        Update project metrics (issue count, progress).
        POST /api/projects/{id}/update_metrics/
        """
        project = self.get_object()
        project.update_metrics()

        return Response({
            'message': 'Metrics updated successfully.',
            'project': ProjectSerializer(project).data
        }, status=status.HTTP_200_OK)
