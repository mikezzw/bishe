from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdoptionApplicationViewSet, AdoptionMatchViewSet

router = DefaultRouter()
router.register(r'applications', AdoptionApplicationViewSet, basename='adoption-application')
router.register(r'matches', AdoptionMatchViewSet, basename='adoption-match')

urlpatterns = [
    path('', include(router.urls)),
]
