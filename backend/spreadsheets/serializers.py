"""
Spreadsheets API Serializers
"""

from rest_framework import serializers
from .models import (
    Spreadsheet, SpreadsheetEditor, Sheet, Cell,
    NamedRange, SpreadsheetSession, SpreadsheetOperation,
    Chart, SpreadsheetComment
)
from users.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization."""

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'avatar_url']
        read_only_fields = fields


class SpreadsheetEditorSerializer(serializers.ModelSerializer):
    """Spreadsheet editor permissions serializer."""

    user = UserBasicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SpreadsheetEditor
        fields = [
            'id', 'user', 'user_id', 'role',
            'added_at', 'last_viewed_at'
        ]
        read_only_fields = ['added_at', 'last_viewed_at']


class SheetSerializer(serializers.ModelSerializer):
    """Sheet serializer."""

    cell_count = serializers.SerializerMethodField()

    class Meta:
        model = Sheet
        fields = [
            'id', 'spreadsheet', 'name', 'position',
            'row_count', 'column_count',
            'frozen_rows', 'frozen_columns',
            'show_grid_lines', 'show_row_headings', 'show_column_headings',
            'is_protected', 'tab_color', 'is_hidden',
            'created_at', 'updated_at', 'cell_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'protection_password': {'write_only': True}
        }

    def get_cell_count(self, obj):
        """Get count of non-empty cells."""
        return obj.cells.exclude(value='').count()


class CellSerializer(serializers.ModelSerializer):
    """Cell serializer."""

    last_modified_by = UserBasicSerializer(read_only=True)
    cell_address = serializers.SerializerMethodField()

    class Meta:
        model = Cell
        fields = [
            'id', 'sheet', 'row', 'column',
            'value', 'formula', 'computed_value',
            'data_type', 'format_config',
            'validation_config', 'note', 'hyperlink',
            'merge_config', 'is_locked', 'version',
            'last_modified_by', 'updated_at',
            'cell_address'
        ]
        read_only_fields = ['computed_value', 'version', 'updated_at']

    def get_cell_address(self, obj):
        """Get Excel-style cell address (e.g., A1, B2)."""
        return str(obj)


class CellBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk cell updates."""

    cells = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )

    def validate_cells(self, value):
        """Validate cell data."""
        for cell_data in value:
            if 'row' not in cell_data or 'column' not in cell_data:
                raise serializers.ValidationError(
                    "Each cell must have 'row' and 'column'"
                )
        return value


class SpreadsheetSerializer(serializers.ModelSerializer):
    """Main spreadsheet serializer."""

    created_by = UserBasicSerializer(read_only=True)
    last_edited_by = UserBasicSerializer(read_only=True)
    editors_data = SpreadsheetEditorSerializer(
        source='spreadsheeteditor_set',
        many=True,
        read_only=True
    )
    sheets = SheetSerializer(many=True, read_only=True)
    active_sessions_count = serializers.SerializerMethodField()

    class Meta:
        model = Spreadsheet
        fields = [
            'id', 'workspace', 'project', 'title', 'slug',
            'created_by', 'last_edited_by',
            'is_template', 'is_archived', 'is_published',
            'permission_level', 'version', 'view_count',
            'created_at', 'updated_at', 'published_at',
            'editors_data', 'sheets', 'active_sessions_count'
        ]
        read_only_fields = [
            'slug', 'created_by', 'last_edited_by',
            'view_count', 'version',
            'created_at', 'updated_at'
        ]

    def get_active_sessions_count(self, obj):
        """Get count of active editing sessions."""
        return obj.active_sessions.filter(is_active=True).count()


class SpreadsheetListSerializer(serializers.ModelSerializer):
    """Lightweight spreadsheet serializer for lists."""

    created_by = UserBasicSerializer(read_only=True)
    last_edited_by = UserBasicSerializer(read_only=True)
    sheet_count = serializers.SerializerMethodField()

    class Meta:
        model = Spreadsheet
        fields = [
            'id', 'title', 'slug',
            'created_by', 'last_edited_by',
            'is_archived', 'permission_level',
            'view_count', 'sheet_count',
            'updated_at', 'created_at'
        ]
        read_only_fields = fields

    def get_sheet_count(self, obj):
        """Get count of sheets."""
        return obj.sheets.count()


class NamedRangeSerializer(serializers.ModelSerializer):
    """Named range serializer."""

    created_by = UserBasicSerializer(read_only=True)
    sheet_name = serializers.CharField(source='sheet.name', read_only=True)

    class Meta:
        model = NamedRange
        fields = [
            'id', 'spreadsheet', 'name', 'sheet', 'sheet_name',
            'start_row', 'start_column', 'end_row', 'end_column',
            'description', 'created_by', 'created_at'
        ]
        read_only_fields = ['created_at']


class ChartSerializer(serializers.ModelSerializer):
    """Chart serializer."""

    created_by = UserBasicSerializer(read_only=True)
    sheet_name = serializers.CharField(source='sheet.name', read_only=True)

    class Meta:
        model = Chart
        fields = [
            'id', 'sheet', 'sheet_name', 'title', 'chart_type',
            'data_range', 'config', 'position',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SpreadsheetCommentSerializer(serializers.ModelSerializer):
    """Spreadsheet comment serializer."""

    author = UserBasicSerializer(read_only=True)
    resolved_by_user = UserBasicSerializer(source='resolved_by', read_only=True)
    replies = serializers.SerializerMethodField()
    cell_address = serializers.SerializerMethodField()

    class Meta:
        model = SpreadsheetComment
        fields = [
            'id', 'sheet', 'author', 'content',
            'row', 'column', 'cell_address',
            'parent_comment',
            'is_resolved', 'resolved_by_user', 'resolved_at',
            'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        """Get comment replies."""
        if obj.parent_comment is None:
            replies = obj.replies.all()
            return SpreadsheetCommentSerializer(replies, many=True).data
        return []

    def get_cell_address(self, obj):
        """Get Excel-style cell address."""
        column_letter = self._column_to_letter(obj.column)
        return f"{column_letter}{obj.row + 1}"

    @staticmethod
    def _column_to_letter(column):
        """Convert column number to Excel-style letter."""
        result = ""
        while column >= 0:
            result = chr(column % 26 + 65) + result
            column = column // 26 - 1
        return result


class SpreadsheetSessionSerializer(serializers.ModelSerializer):
    """Active spreadsheet session serializer."""

    user = UserBasicSerializer(read_only=True)
    active_sheet_name = serializers.CharField(
        source='active_sheet.name',
        read_only=True
    )

    class Meta:
        model = SpreadsheetSession
        fields = [
            'id', 'spreadsheet', 'user', 'session_id',
            'is_active', 'selected_cell', 'selected_range',
            'user_color', 'active_sheet', 'active_sheet_name',
            'joined_at', 'last_activity_at'
        ]
        read_only_fields = [
            'session_id', 'user_color',
            'joined_at', 'last_activity_at'
        ]


class SpreadsheetOperationSerializer(serializers.ModelSerializer):
    """Spreadsheet operation serializer."""

    session = SpreadsheetSessionSerializer(read_only=True)

    class Meta:
        model = SpreadsheetOperation
        fields = [
            'id', 'spreadsheet', 'session',
            'operation_type', 'operation_data',
            'base_version', 'sequence_number',
            'is_acknowledged', 'acknowledged_at',
            'created_at'
        ]
        read_only_fields = ['created_at']
