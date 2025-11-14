"""
Spreadsheets Admin Interface
"""

from django.contrib import admin
from .models import (
    Spreadsheet, SpreadsheetEditor, Sheet, Cell,
    NamedRange, SpreadsheetSession, SpreadsheetOperation,
    Chart, SpreadsheetComment
)


@admin.register(Spreadsheet)
class SpreadsheetAdmin(admin.ModelAdmin):
    """Admin interface for spreadsheets."""

    list_display = [
        'title', 'workspace', 'created_by',
        'is_archived', 'is_published', 'permission_level',
        'version', 'view_count', 'updated_at'
    ]
    list_filter = [
        'is_archived', 'is_published',
        'permission_level', 'created_at'
    ]
    search_fields = ['title', 'slug']
    readonly_fields = [
        'slug', 'version', 'view_count',
        'created_at', 'updated_at'
    ]
    raw_id_fields = ['workspace', 'project', 'created_by', 'last_edited_by']
    date_hierarchy = 'created_at'
    ordering = ['-updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'workspace', 'project')
        }),
        ('Ownership', {
            'fields': ('created_by', 'last_edited_by')
        }),
        ('Status', {
            'fields': ('is_template', 'is_archived', 'is_published', 'published_at', 'permission_level')
        }),
        ('Metadata', {
            'fields': ('version', 'view_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(SpreadsheetEditor)
class SpreadsheetEditorAdmin(admin.ModelAdmin):
    """Admin interface for spreadsheet editors."""

    list_display = ['spreadsheet', 'user', 'role', 'added_at', 'last_viewed_at']
    list_filter = ['role', 'added_at']
    search_fields = ['spreadsheet__title', 'user__email']
    raw_id_fields = ['spreadsheet', 'user']
    date_hierarchy = 'added_at'


@admin.register(Sheet)
class SheetAdmin(admin.ModelAdmin):
    """Admin interface for sheets."""

    list_display = [
        'name', 'spreadsheet', 'position',
        'row_count', 'column_count', 'is_protected',
        'is_hidden', 'tab_color'
    ]
    list_filter = ['is_protected', 'is_hidden', 'created_at']
    search_fields = ['name', 'spreadsheet__title']
    raw_id_fields = ['spreadsheet']
    ordering = ['spreadsheet', 'position']

    fieldsets = (
        ('Basic Information', {
            'fields': ('spreadsheet', 'name', 'position')
        }),
        ('Dimensions', {
            'fields': ('row_count', 'column_count', 'frozen_rows', 'frozen_columns')
        }),
        ('Display', {
            'fields': ('show_grid_lines', 'show_row_headings', 'show_column_headings', 'tab_color')
        }),
        ('Protection', {
            'fields': ('is_protected', 'protection_password', 'is_hidden')
        }),
    )


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    """Admin interface for cells."""

    list_display = [
        'cell_address', 'sheet', 'value_preview',
        'data_type', 'last_modified_by', 'updated_at'
    ]
    list_filter = ['data_type', 'is_locked', 'updated_at']
    search_fields = ['sheet__name', 'value', 'formula']
    raw_id_fields = ['sheet', 'last_modified_by']
    date_hierarchy = 'updated_at'

    def cell_address(self, obj):
        """Show cell address (e.g., A1)."""
        return str(obj)
    cell_address.short_description = 'Address'

    def value_preview(self, obj):
        """Show preview of cell value."""
        return obj.value[:30] + '...' if len(obj.value) > 30 else obj.value
    value_preview.short_description = 'Value'


@admin.register(NamedRange)
class NamedRangeAdmin(admin.ModelAdmin):
    """Admin interface for named ranges."""

    list_display = [
        'name', 'spreadsheet', 'sheet',
        'start_row', 'start_column', 'end_row', 'end_column',
        'created_by', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'spreadsheet__title']
    raw_id_fields = ['spreadsheet', 'sheet', 'created_by']
    date_hierarchy = 'created_at'


@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    """Admin interface for charts."""

    list_display = [
        'title', 'chart_type', 'sheet',
        'created_by', 'created_at'
    ]
    list_filter = ['chart_type', 'created_at']
    search_fields = ['title', 'sheet__name']
    raw_id_fields = ['sheet', 'created_by']
    date_hierarchy = 'created_at'


@admin.register(SpreadsheetComment)
class SpreadsheetCommentAdmin(admin.ModelAdmin):
    """Admin interface for spreadsheet comments."""

    list_display = [
        'sheet', 'cell_address', 'author',
        'content_preview', 'is_resolved', 'created_at'
    ]
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['sheet__name', 'author__email', 'content']
    raw_id_fields = ['sheet', 'author', 'parent_comment', 'resolved_by']
    date_hierarchy = 'created_at'

    def cell_address(self, obj):
        """Show cell address."""
        column_letter = self._column_to_letter(obj.column)
        return f"{column_letter}{obj.row + 1}"
    cell_address.short_description = 'Cell'

    def content_preview(self, obj):
        """Show preview of comment content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    @staticmethod
    def _column_to_letter(column):
        """Convert column number to Excel-style letter."""
        result = ""
        while column >= 0:
            result = chr(column % 26 + 65) + result
            column = column // 26 - 1
        return result


@admin.register(SpreadsheetSession)
class SpreadsheetSessionAdmin(admin.ModelAdmin):
    """Admin interface for spreadsheet sessions."""

    list_display = [
        'spreadsheet', 'user', 'session_id',
        'is_active', 'active_sheet', 'user_color',
        'joined_at', 'last_activity_at'
    ]
    list_filter = ['is_active', 'joined_at']
    search_fields = ['spreadsheet__title', 'user__email', 'session_id']
    raw_id_fields = ['spreadsheet', 'user', 'active_sheet']
    date_hierarchy = 'joined_at'
    readonly_fields = ['session_id', 'joined_at', 'last_activity_at']


@admin.register(SpreadsheetOperation)
class SpreadsheetOperationAdmin(admin.ModelAdmin):
    """Admin interface for spreadsheet operations."""

    list_display = [
        'spreadsheet', 'operation_type', 'base_version',
        'sequence_number', 'is_acknowledged', 'created_at'
    ]
    list_filter = ['operation_type', 'is_acknowledged', 'created_at']
    search_fields = ['spreadsheet__title']
    raw_id_fields = ['spreadsheet', 'session']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
