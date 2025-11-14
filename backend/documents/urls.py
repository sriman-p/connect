"""
Documents URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet, DocumentFolderViewSet, DocumentCommentViewSet,
    DocumentTemplateViewSet
)

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'folders', DocumentFolderViewSet, basename='document-folder')
router.register(r'comments', DocumentCommentViewSet, basename='document-comment')
router.register(r'templates', DocumentTemplateViewSet, basename='document-template')

urlpatterns = [
    path('', include(router.urls)),
]
