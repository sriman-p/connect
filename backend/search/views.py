"""
Search Views
Simple cross-platform search service
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Q
from projects.models import Project
from issues.models import Issue
from documents.models import Document
from workspaces.models import Workspace


class SearchView(APIView):
    """Global search across all content types."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Perform search."""
        query = request.GET.get('q', '').strip()

        if not query or len(query) < 2:
            return Response({
                'error': 'Query must be at least 2 characters'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        workspace_ids = user.workspace_memberships.values_list('workspace_id', flat=True)

        # Search projects
        projects = Project.objects.filter(
            workspace_id__in=workspace_ids
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:10]

        # Search issues
        issues = Issue.objects.filter(
            workspace_id__in=workspace_ids
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:20]

        # Search documents
        documents = Document.objects.filter(
            workspace_id__in=workspace_ids
        ).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )[:20]

        # Search workspaces
        workspaces = Workspace.objects.filter(
            id__in=workspace_ids
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:10]

        results = {
            'query': query,
            'projects': [{
                'id': p.id,
                'name': p.name,
                'description': p.description[:200] if p.description else '',
                'type': 'project'
            } for p in projects],
            'issues': [{
                'id': i.id,
                'title': i.title,
                'description': i.description[:200] if i.description else '',
                'status': i.status,
                'type': 'issue'
            } for i in issues],
            'documents': [{
                'id': d.id,
                'title': d.title,
                'content': d.content[:200] if d.content else '',
                'type': 'document'
            } for d in documents],
            'workspaces': [{
                'id': w.id,
                'name': w.name,
                'description': w.description[:200] if w.description else '',
                'type': 'workspace'
            } for w in workspaces],
            'total_results': len(projects) + len(issues) + len(documents) + len(workspaces)
        }

        return Response(results)
