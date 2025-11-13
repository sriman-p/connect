from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabelViewSet, IssueViewSet, IssueCommentViewSet

app_name = 'issues'

# Create router
router = DefaultRouter()
router.register(r'labels', LabelViewSet, basename='label')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'issue-comments', IssueCommentViewSet, basename='issue-comment')

urlpatterns = router.urls
