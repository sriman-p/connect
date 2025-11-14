"""
AI Views
"""

import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AIInteraction, AISmartSuggestion, AIModelConfig
from .serializers import (
    AIInteractionSerializer,
    AISmartSuggestionSerializer,
    AIModelConfigSerializer,
    CompletionRequestSerializer,
    SummaryRequestSerializer,
    SuggestionRequestSerializer,
    AnalysisRequestSerializer,
    TranslationRequestSerializer,
    CodeReviewRequestSerializer,
    ChatRequestSerializer,
)
from .gemini_service import get_gemini_service

logger = logging.getLogger(__name__)


class AIInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for AI interactions."""

    serializer_class = AIInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return interactions for user's workspaces."""
        user = self.request.user
        return AIInteraction.objects.filter(
            workspace__members=user
        ).select_related('workspace', 'user').distinct()

    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate an AI interaction."""
        interaction = self.get_object()
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')

        if rating and 1 <= rating <= 5:
            interaction.rating = rating
            interaction.feedback = feedback
            interaction.save()

            return Response({
                'status': 'success',
                'message': 'Rating saved'
            })

        return Response({
            'status': 'error',
            'message': 'Invalid rating (must be 1-5)'
        }, status=status.HTTP_400_BAD_REQUEST)


class AISmartSuggestionViewSet(viewsets.ModelViewSet):
    """ViewSet for AI smart suggestions."""

    serializer_class = AISmartSuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return suggestions for user's workspaces."""
        user = self.request.user
        return AISmartSuggestion.objects.filter(
            workspace__members=user
        ).select_related('workspace', 'user').distinct()

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a suggestion."""
        suggestion = self.get_object()
        suggestion.status = 'accepted'
        from django.utils import timezone
        suggestion.accepted_at = timezone.now()
        suggestion.save()

        return Response({
            'status': 'success',
            'message': 'Suggestion accepted'
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a suggestion."""
        suggestion = self.get_object()
        suggestion.status = 'rejected'
        suggestion.save()

        return Response({
            'status': 'success',
            'message': 'Suggestion rejected'
        })


class AIModelConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for AI model configuration."""

    serializer_class = AIModelConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return configs for user's workspaces."""
        user = self.request.user
        return AIModelConfig.objects.filter(
            workspace__members=user
        ).select_related('workspace').distinct()


class AIServiceViewSet(viewsets.ViewSet):
    """ViewSet for AI service endpoints."""

    permission_classes = [permissions.IsAuthenticated]

    def _get_workspace(self, request):
        """Get workspace from request."""
        workspace_id = request.data.get('workspace_id')
        if not workspace_id:
            return None

        from workspaces.models import Workspace
        try:
            return Workspace.objects.get(id=workspace_id, members=request.user)
        except Workspace.DoesNotExist:
            return None

    @action(detail=False, methods=['post'])
    def complete(self, request):
        """Generate text completion."""
        serializer = CompletionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        workspace = self._get_workspace(request)

        try:
            service = get_gemini_service(workspace=workspace)
            result = service.generate_completion(
                prompt=serializer.validated_data['prompt'],
                user=request.user,
                temperature=serializer.validated_data.get('temperature', 0.7),
                max_tokens=serializer.validated_data.get('max_tokens'),
                context=serializer.validated_data.get('context')
            )

            if result['success']:
                return Response(result)
            else:
                return Response(
                    {'error': result.get('error', 'Unknown error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"AI completion error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def summarize(self, request):
        """Generate content summary."""
        serializer = SummaryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        workspace = self._get_workspace(request)

        try:
            service = get_gemini_service(workspace=workspace)
            result = service.generate_summary(
                content=serializer.validated_data['content'],
                user=request.user,
                max_length=serializer.validated_data.get('max_length', 200)
            )

            if result['success']:
                return Response(result)
            else:
                return Response(
                    {'error': result.get('error', 'Unknown error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"AI summary error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def suggest(self, request):
        """Generate smart suggestions."""
        serializer = SuggestionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        workspace = self._get_workspace(request)

        try:
            service = get_gemini_service(workspace=workspace)
            result = service.generate_suggestions(
                context=serializer.validated_data['context'],
                suggestion_type=serializer.validated_data['suggestion_type'],
                user=request.user,
                count=serializer.validated_data.get('count', 3)
            )

            if result['success']:
                return Response(result)
            else:
                return Response(
                    {'error': result.get('error', 'Unknown error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"AI suggestion error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze content."""
        serializer = AnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        workspace = self._get_workspace(request)

        try:
            service = get_gemini_service(workspace=workspace)
            result = service.analyze_content(
                content=serializer.validated_data['content'],
                analysis_type=serializer.validated_data['analysis_type'],
                user=request.user
            )

            if result['success']:
                return Response(result)
            else:
                return Response(
                    {'error': result.get('error', 'Unknown error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def translate(self, request):
        """Translate content."""
        serializer = TranslationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        workspace = self._get_workspace(request)

        try:
            service = get_gemini_service(workspace=workspace)
            result = service.translate_content(
                content=serializer.validated_data['content'],
                target_language=serializer.validated_data['target_language'],
                user=request.user
            )

            if result['success']:
                return Response(result)
            else:
                return Response(
                    {'error': result.get('error', 'Unknown error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"AI translation error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def review_code(self, request):
        """Review code."""
        serializer = CodeReviewRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        workspace = self._get_workspace(request)

        try:
            service = get_gemini_service(workspace=workspace)
            result = service.review_code(
                code=serializer.validated_data['code'],
                language=serializer.validated_data['language'],
                user=request.user
            )

            if result['success']:
                return Response(result)
            else:
                return Response(
                    {'error': result.get('error', 'Unknown error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"AI code review error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def chat(self, request):
        """Multi-turn chat conversation."""
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        workspace = self._get_workspace(request)

        try:
            service = get_gemini_service(workspace=workspace)
            result = service.chat(
                messages=serializer.validated_data['messages'],
                user=request.user
            )

            if result['success']:
                return Response(result)
            else:
                return Response(
                    {'error': result.get('error', 'Unknown error')},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"AI chat error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
