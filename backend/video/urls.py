"""
Video Conferencing URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VideoRoomViewSet,
    VideoParticipantViewSet,
    VideoRecordingViewSet,
    VideoInvitationViewSet,
)

router = DefaultRouter()
router.register(r'rooms', VideoRoomViewSet, basename='video-room')
router.register(r'participants', VideoParticipantViewSet, basename='video-participant')
router.register(r'recordings', VideoRecordingViewSet, basename='video-recording')
router.register(r'invitations', VideoInvitationViewSet, basename='video-invitation')

urlpatterns = [
    path('', include(router.urls)),
]
