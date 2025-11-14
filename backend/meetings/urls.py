"""
Meetings URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeetingViewSet, MeetingNoteViewSet, MeetingRecordingViewSet

app_name = 'meetings'

router = DefaultRouter()
router.register(r'meetings', MeetingViewSet, basename='meeting')
router.register(r'meeting-notes', MeetingNoteViewSet, basename='meeting-note')
router.register(r'meeting-recordings', MeetingRecordingViewSet, basename='meeting-recording')

urlpatterns = [
    path('', include(router.urls)),
]
