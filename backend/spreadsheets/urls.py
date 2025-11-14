"""
Spreadsheets URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SpreadsheetViewSet, SheetViewSet, CellViewSet,
    NamedRangeViewSet, ChartViewSet, SpreadsheetCommentViewSet
)

router = DefaultRouter()
router.register(r'spreadsheets', SpreadsheetViewSet, basename='spreadsheet')
router.register(r'sheets', SheetViewSet, basename='sheet')
router.register(r'cells', CellViewSet, basename='cell')
router.register(r'named-ranges', NamedRangeViewSet, basename='named-range')
router.register(r'charts', ChartViewSet, basename='chart')
router.register(r'comments', SpreadsheetCommentViewSet, basename='spreadsheet-comment')

urlpatterns = [
    path('', include(router.urls)),
]
