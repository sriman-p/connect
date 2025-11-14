"""
Files URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FileViewSet,
    FileFolderViewSet,
    FileShareViewSet,
    FileVersionViewSet,
)

app_name = 'files'

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')
router.register(r'folders', FileFolderViewSet, basename='folder')
router.register(r'shares', FileShareViewSet, basename='share')
router.register(r'versions', FileVersionViewSet, basename='version')

urlpatterns = [
    path('', include(router.urls)),
]
