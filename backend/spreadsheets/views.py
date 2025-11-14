"""
Spreadsheets API Views
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import (
    Spreadsheet, SpreadsheetEditor, Sheet, Cell,
    NamedRange, SpreadsheetSession, Chart, SpreadsheetComment
)
from .serializers import (
    SpreadsheetSerializer, SpreadsheetListSerializer, SpreadsheetEditorSerializer,
    SheetSerializer, CellSerializer, CellBulkUpdateSerializer,
    NamedRangeSerializer, ChartSerializer, SpreadsheetCommentSerializer,
    SpreadsheetSessionSerializer
)


class SpreadsheetViewSet(viewsets.ModelViewSet):
    """Spreadsheet CRUD operations."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workspace', 'project', 'is_archived', 'permission_level']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return SpreadsheetListSerializer
        return SpreadsheetSerializer

    def get_queryset(self):
        """Filter spreadsheets by user access."""
        user = self.request.user
        return Spreadsheet.objects.filter(
            Q(created_by=user) |
            Q(editors__user=user) |
            Q(permission_level__in=['workspace', 'public'])
        ).select_related(
            'created_by', 'last_edited_by'
        ).prefetch_related(
            'editors', 'sheets'
        ).distinct()

    def perform_create(self, serializer):
        """Set created_by and create default sheet when creating spreadsheet."""
        spreadsheet = serializer.save(created_by=self.request.user)

        # Create default sheet
        Sheet.objects.create(
            spreadsheet=spreadsheet,
            name='Sheet1',
            position=0
        )

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a spreadsheet."""
        spreadsheet = self.get_object()
        new_spreadsheet = Spreadsheet.objects.create(
            workspace=spreadsheet.workspace,
            project=spreadsheet.project,
            title=f"{spreadsheet.title} (Copy)",
            created_by=request.user,
            permission_level=spreadsheet.permission_level
        )

        # Copy sheets
        for sheet in spreadsheet.sheets.all():
            new_sheet = Sheet.objects.create(
                spreadsheet=new_spreadsheet,
                name=sheet.name,
                position=sheet.position,
                row_count=sheet.row_count,
                column_count=sheet.column_count,
                frozen_rows=sheet.frozen_rows,
                frozen_columns=sheet.frozen_columns,
                tab_color=sheet.tab_color
            )

            # Copy cells
            for cell in sheet.cells.all():
                Cell.objects.create(
                    sheet=new_sheet,
                    row=cell.row,
                    column=cell.column,
                    value=cell.value,
                    formula=cell.formula,
                    data_type=cell.data_type,
                    format_config=cell.format_config,
                    last_modified_by=request.user
                )

        serializer = self.get_serializer(new_spreadsheet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a spreadsheet."""
        spreadsheet = self.get_object()
        spreadsheet.is_archived = True
        spreadsheet.save()
        return Response({'status': 'archived'})

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a spreadsheet."""
        spreadsheet = self.get_object()
        spreadsheet.is_archived = False
        spreadsheet.save()
        return Response({'status': 'unarchived'})

    @action(detail=True, methods=['get'])
    def active_sessions(self, request, pk=None):
        """Get active editing sessions."""
        spreadsheet = self.get_object()
        sessions = spreadsheet.active_sessions.filter(is_active=True)
        serializer = SpreadsheetSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_editor(self, request, pk=None):
        """Add an editor to the spreadsheet."""
        spreadsheet = self.get_object()
        serializer = SpreadsheetEditorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(spreadsheet=spreadsheet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_editor(self, request, pk=None):
        """Remove an editor from the spreadsheet."""
        spreadsheet = self.get_object()
        user_id = request.data.get('user_id')
        SpreadsheetEditor.objects.filter(
            spreadsheet=spreadsheet,
            user_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SheetViewSet(viewsets.ModelViewSet):
    """Sheet operations."""

    serializer_class = SheetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['spreadsheet']

    def get_queryset(self):
        """Filter sheets by spreadsheet access."""
        user = self.request.user
        return Sheet.objects.filter(
            spreadsheet__in=Spreadsheet.objects.filter(
                Q(created_by=user) |
                Q(editors__user=user) |
                Q(permission_level__in=['workspace', 'public'])
            )
        ).select_related('spreadsheet')

    @action(detail=True, methods=['get'])
    def cells(self, request, pk=None):
        """Get all cells in a sheet."""
        sheet = self.get_object()

        # Support pagination and filtering
        row_start = request.query_params.get('row_start', 0)
        row_end = request.query_params.get('row_end', sheet.row_count)
        col_start = request.query_params.get('col_start', 0)
        col_end = request.query_params.get('col_end', sheet.column_count)

        cells = sheet.cells.filter(
            row__gte=row_start,
            row__lt=row_end,
            column__gte=col_start,
            column__lt=col_end
        ).select_related('last_modified_by')

        serializer = CellSerializer(cells, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a sheet."""
        sheet = self.get_object()
        new_position = sheet.spreadsheet.sheets.count()
        new_sheet = Sheet.objects.create(
            spreadsheet=sheet.spreadsheet,
            name=f"{sheet.name} (Copy)",
            position=new_position,
            row_count=sheet.row_count,
            column_count=sheet.column_count,
            frozen_rows=sheet.frozen_rows,
            frozen_columns=sheet.frozen_columns,
            tab_color=sheet.tab_color
        )

        # Copy cells
        for cell in sheet.cells.all():
            Cell.objects.create(
                sheet=new_sheet,
                row=cell.row,
                column=cell.column,
                value=cell.value,
                formula=cell.formula,
                data_type=cell.data_type,
                format_config=cell.format_config,
                last_modified_by=request.user
            )

        serializer = self.get_serializer(new_sheet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CellViewSet(viewsets.ModelViewSet):
    """Cell operations."""

    serializer_class = CellSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sheet']

    def get_queryset(self):
        """Filter cells by sheet access."""
        user = self.request.user
        return Cell.objects.filter(
            sheet__spreadsheet__in=Spreadsheet.objects.filter(
                Q(created_by=user) |
                Q(editors__user=user) |
                Q(permission_level__in=['workspace', 'public'])
            )
        ).select_related('sheet', 'last_modified_by')

    def perform_create(self, serializer):
        """Set last_modified_by when creating cell."""
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        """Set last_modified_by when updating cell."""
        serializer.save(last_modified_by=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update multiple cells."""
        serializer = CellBulkUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cells_data = serializer.validated_data['cells']
        sheet_id = request.data.get('sheet_id')

        if not sheet_id:
            return Response(
                {'error': 'sheet_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_cells = []
        for cell_data in cells_data:
            cell, created = Cell.objects.update_or_create(
                sheet_id=sheet_id,
                row=cell_data['row'],
                column=cell_data['column'],
                defaults={
                    'value': cell_data.get('value', ''),
                    'formula': cell_data.get('formula', ''),
                    'data_type': cell_data.get('data_type', 'text'),
                    'format_config': cell_data.get('format_config', {}),
                    'last_modified_by': request.user
                }
            )
            updated_cells.append(cell)

        serializer = CellSerializer(updated_cells, many=True)
        return Response(serializer.data)


class NamedRangeViewSet(viewsets.ModelViewSet):
    """Named range operations."""

    serializer_class = NamedRangeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['spreadsheet', 'sheet']

    def get_queryset(self):
        """Filter named ranges by spreadsheet access."""
        user = self.request.user
        return NamedRange.objects.filter(
            spreadsheet__in=Spreadsheet.objects.filter(
                Q(created_by=user) |
                Q(editors__user=user) |
                Q(permission_level__in=['workspace', 'public'])
            )
        ).select_related('spreadsheet', 'sheet', 'created_by')

    def perform_create(self, serializer):
        """Set created_by when creating named range."""
        serializer.save(created_by=self.request.user)


class ChartViewSet(viewsets.ModelViewSet):
    """Chart operations."""

    serializer_class = ChartSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sheet']

    def get_queryset(self):
        """Filter charts by sheet access."""
        user = self.request.user
        return Chart.objects.filter(
            sheet__spreadsheet__in=Spreadsheet.objects.filter(
                Q(created_by=user) |
                Q(editors__user=user) |
                Q(permission_level__in=['workspace', 'public'])
            )
        ).select_related('sheet', 'created_by')

    def perform_create(self, serializer):
        """Set created_by when creating chart."""
        serializer.save(created_by=self.request.user)


class SpreadsheetCommentViewSet(viewsets.ModelViewSet):
    """Spreadsheet comment operations."""

    serializer_class = SpreadsheetCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sheet', 'is_resolved']

    def get_queryset(self):
        """Filter comments by sheet access."""
        user = self.request.user
        return SpreadsheetComment.objects.filter(
            sheet__spreadsheet__in=Spreadsheet.objects.filter(
                Q(created_by=user) |
                Q(editors__user=user) |
                Q(permission_level__in=['workspace', 'public'])
            )
        ).select_related('author', 'resolved_by', 'sheet')

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
