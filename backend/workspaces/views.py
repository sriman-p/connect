from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Workspace, WorkspaceMember
from .serializers import (
    WorkspaceSerializer,
    WorkspaceMemberSerializer,
    WorkspaceMemberInviteSerializer,
    WorkspaceMemberUpdateSerializer,
)

User = get_user_model()


class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Workspace CRUD operations.
    Endpoints:
    - GET /api/workspaces/ - List user's workspaces
    - POST /api/workspaces/ - Create workspace
    - GET /api/workspaces/{id}/ - Get workspace details
    - PATCH /api/workspaces/{id}/ - Update workspace
    - DELETE /api/workspaces/{id}/ - Delete workspace
    """

    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return workspaces where user is a member."""
        user = self.request.user
        return Workspace.objects.filter(
            members__user=user,
            members__is_active=True,
            is_active=True
        ).distinct()

    def perform_create(self, serializer):
        """Create workspace and add creator as owner with full permissions."""
        workspace = serializer.save(owner=self.request.user)

        # Add creator as member with owner role and all permissions
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=self.request.user,
            role=WorkspaceMember.OWNER,
            permissions=(1 << 64) - 1,  # All permissions
            is_active=True
        )

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        Get all members of a workspace.
        GET /api/workspaces/{id}/members/
        """
        workspace = self.get_object()
        members = WorkspaceMember.objects.filter(
            workspace=workspace,
            is_active=True
        ).select_related('user')

        serializer = WorkspaceMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """
        Invite a user to workspace.
        POST /api/workspaces/{id}/invite/
        Body: {"email": "user@example.com", "role": "member"}
        """
        workspace = self.get_object()
        serializer = WorkspaceMemberInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email'].lower()
        role = serializer.validated_data['role']

        # Get user
        user = User.objects.get(email=email)

        # Check if already a member
        if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
            return Response({
                'error': 'User is already a member of this workspace.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create membership
        member = WorkspaceMember.objects.create(
            workspace=workspace,
            user=user,
            role=role,
            is_active=True
        )
        member.set_role_permissions()

        return Response({
            'message': f'{user.email} has been invited to the workspace.',
            'member': WorkspaceMemberSerializer(member).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """
        Leave a workspace.
        POST /api/workspaces/{id}/leave/
        """
        workspace = self.get_object()
        user = request.user

        # Can't leave if you're the owner
        if workspace.owner == user:
            return Response({
                'error': 'Workspace owner cannot leave. Transfer ownership first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Remove membership
        WorkspaceMember.objects.filter(
            workspace=workspace,
            user=user
        ).update(is_active=False)

        return Response({
            'message': 'You have left the workspace.'
        }, status=status.HTTP_200_OK)


class WorkspaceMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkspaceMember management.
    Endpoints:
    - GET /api/workspace-members/ - List memberships
    - GET /api/workspace-members/{id}/ - Get member details
    - PATCH /api/workspace-members/{id}/ - Update member (role/permissions)
    - DELETE /api/workspace-members/{id}/ - Remove member
    """

    serializer_class = WorkspaceMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return members of workspaces where user has access."""
        user = self.request.user
        return WorkspaceMember.objects.filter(
            workspace__members__user=user,
            workspace__is_active=True,
            is_active=True
        ).distinct().select_related('user', 'workspace')

    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.action in ['update', 'partial_update']:
            return WorkspaceMemberUpdateSerializer
        return WorkspaceMemberSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete membership."""
        instance = self.get_object()

        # Can't remove workspace owner
        if instance.workspace.owner == instance.user:
            return Response({
                'error': 'Cannot remove workspace owner.'
            }, status=status.HTTP_400_BAD_REQUEST)

        instance.is_active = False
        instance.save()

        return Response({
            'message': 'Member removed from workspace.'
        }, status=status.HTTP_200_OK)
