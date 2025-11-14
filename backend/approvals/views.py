"""
Approvals Views
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ApprovalWorkflow, ApprovalStep, ApprovalRequest, ApprovalAction
from .serializers import (
    ApprovalWorkflowSerializer,
    ApprovalWorkflowListSerializer,
    ApprovalStepSerializer,
    ApprovalRequestSerializer,
    ApprovalRequestListSerializer,
    ApprovalRequestCreateSerializer,
    ApprovalActionSerializer,
)


class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for approval workflows."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return ApprovalWorkflowListSerializer
        return ApprovalWorkflowSerializer

    def get_queryset(self):
        """Return workflows for user's workspaces."""
        user = self.request.user
        return ApprovalWorkflow.objects.filter(
            workspace__members=user
        ).select_related('created_by', 'workspace').prefetch_related(
            'steps'
        ).distinct()

    def perform_create(self, serializer):
        """Set creator to current user."""
        serializer.save(created_by=self.request.user)


class ApprovalStepViewSet(viewsets.ModelViewSet):
    """ViewSet for approval steps."""

    serializer_class = ApprovalStepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return steps for user's workflows."""
        user = self.request.user
        return ApprovalStep.objects.filter(
            workflow__workspace__members=user
        ).select_related('workflow').prefetch_related('approvers').distinct()


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for approval requests."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return ApprovalRequestListSerializer
        elif self.action == 'create':
            return ApprovalRequestCreateSerializer
        return ApprovalRequestSerializer

    def get_queryset(self):
        """Return approval requests for user."""
        user = self.request.user
        return ApprovalRequest.objects.filter(
            workspace__members=user
        ).select_related(
            'requester', 'workflow', 'workspace'
        ).prefetch_related('actions').distinct()

    def perform_create(self, serializer):
        """Set requester to current user."""
        serializer.save(requester=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a request."""
        approval_request = self.get_object()
        step_id = request.data.get('step_id')
        comments = request.data.get('comments', '')

        # Create approval action
        ApprovalAction.objects.create(
            approval_request=approval_request,
            step_id=step_id,
            approver=request.user,
            action='approved',
            comments=comments
        )

        # Check if all steps are approved
        total_steps = approval_request.workflow.steps.count()
        approved_steps = approval_request.actions.filter(
            action='approved'
        ).values('step_id').distinct().count()

        if approved_steps >= total_steps:
            approval_request.status = 'approved'
            approval_request.approved_at = timezone.now()
            approval_request.save()

        return Response({
            'message': 'Request approved.',
            'request': ApprovalRequestSerializer(approval_request).data
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a request."""
        approval_request = self.get_object()
        step_id = request.data.get('step_id')
        comments = request.data.get('comments', '')

        # Create rejection action
        ApprovalAction.objects.create(
            approval_request=approval_request,
            step_id=step_id,
            approver=request.user,
            action='rejected',
            comments=comments
        )

        approval_request.status = 'rejected'
        approval_request.rejected_at = timezone.now()
        approval_request.save()

        return Response({
            'message': 'Request rejected.',
            'request': ApprovalRequestSerializer(approval_request).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a request."""
        approval_request = self.get_object()

        if approval_request.requester != request.user:
            return Response({
                'error': 'Only the requester can cancel this request.'
            }, status=status.HTTP_403_FORBIDDEN)

        approval_request.status = 'cancelled'
        approval_request.save()

        return Response({
            'message': 'Request cancelled.',
            'request': ApprovalRequestSerializer(approval_request).data
        })


class ApprovalActionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for approval actions (read-only)."""

    serializer_class = ApprovalActionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return actions for user's approval requests."""
        user = self.request.user
        return ApprovalAction.objects.filter(
            approval_request__workspace__members=user
        ).select_related(
            'approval_request', 'step', 'approver', 'delegated_to'
        ).distinct()
