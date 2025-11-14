"""
Approvals Serializers
"""

from rest_framework import serializers
from django.utils import timezone
from .models import ApprovalWorkflow, ApprovalStep, ApprovalRequest, ApprovalAction
from users.serializers import UserSerializer


class ApprovalStepSerializer(serializers.ModelSerializer):
    """Serializer for approval steps."""

    approvers = UserSerializer(many=True, read_only=True)
    approver_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = ApprovalStep
        fields = [
            'id', 'workflow', 'name', 'description', 'order',
            'approvers', 'approver_ids', 'required_approvals',
            'allow_delegation'
        ]
        read_only_fields = ['id']


class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for approval workflows."""

    created_by = UserSerializer(read_only=True)
    steps = ApprovalStepSerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalWorkflow
        fields = [
            'id', 'workspace', 'name', 'description',
            'workflow_type', 'auto_approve_after_hours',
            'is_active', 'created_by', 'steps',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ApprovalWorkflowListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for workflow lists."""

    created_by = UserSerializer(read_only=True)
    step_count = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalWorkflow
        fields = [
            'id', 'name', 'workflow_type', 'is_active',
            'created_by', 'step_count', 'created_at'
        ]

    def get_step_count(self, obj):
        """Get number of steps."""
        return obj.steps.count()


class ApprovalActionSerializer(serializers.ModelSerializer):
    """Serializer for approval actions."""

    approver = UserSerializer(read_only=True)
    delegated_to = UserSerializer(read_only=True)

    class Meta:
        model = ApprovalAction
        fields = [
            'id', 'approval_request', 'step', 'approver',
            'action', 'comments', 'delegated_to', 'created_at'
        ]
        read_only_fields = ['id', 'approver', 'created_at']


class ApprovalRequestSerializer(serializers.ModelSerializer):
    """Full serializer for approval requests."""

    requester = UserSerializer(read_only=True)
    workflow = ApprovalWorkflowSerializer(read_only=True)
    actions = ApprovalActionSerializer(many=True, read_only=True)
    current_step = serializers.SerializerMethodField()

    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'workspace', 'workflow', 'title', 'description',
            'priority', 'requester', 'status', 'due_date',
            'related_object_type', 'related_object_id',
            'actions', 'current_step', 'created_at', 'updated_at',
            'submitted_at', 'approved_at', 'rejected_at'
        ]
        read_only_fields = [
            'id', 'requester', 'status', 'created_at', 'updated_at',
            'submitted_at', 'approved_at', 'rejected_at'
        ]

    def get_current_step(self, obj):
        """Get current approval step."""
        if obj.status == 'pending':
            # Find the next step that needs approval
            completed_steps = obj.actions.filter(
                action='approved'
            ).values_list('step_id', flat=True)

            next_step = obj.workflow.steps.exclude(
                id__in=completed_steps
            ).order_by('order').first()

            if next_step:
                return ApprovalStepSerializer(next_step).data

        return None


class ApprovalRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for approval request lists."""

    requester = UserSerializer(read_only=True)
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = [
            'id', 'title', 'workflow_name', 'status',
            'priority', 'requester', 'due_date', 'created_at'
        ]


class ApprovalRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating approval requests."""

    class Meta:
        model = ApprovalRequest
        fields = [
            'workspace', 'workflow', 'title', 'description',
            'priority', 'due_date', 'related_object_type',
            'related_object_id'
        ]

    def create(self, validated_data):
        """Create approval request."""
        request = ApprovalRequest.objects.create(**validated_data)
        request.status = 'pending'
        request.submitted_at = timezone.now()
        request.save()
        return request
