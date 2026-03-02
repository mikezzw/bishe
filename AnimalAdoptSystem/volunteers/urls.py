from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VolunteerProfileViewSet, VolunteerTaskViewSet, VolunteerActivityViewSet, ActivityParticipantViewSet

router = DefaultRouter()
router.register(r'profiles', VolunteerProfileViewSet, basename='volunteer-profile')
router.register(r'tasks', VolunteerTaskViewSet, basename='volunteer-task')
router.register(r'activities', VolunteerActivityViewSet, basename='volunteer-activity')
router.register(r'participants', ActivityParticipantViewSet, basename='activity-participant')

urlpatterns = [
    path('', include(router.urls)),
]
