from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, NotificationViewSet, ReportViewSet, ContentModerationViewSet, UserFeedbackViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'moderation', ContentModerationViewSet, basename='moderation')
router.register(r'feedbacks', UserFeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]
