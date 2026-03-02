from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShelterViewSet, ShelterStaffViewSet, DonationViewSet, InteractionApplicationViewSet, ShelterActivityViewSet, DonationUsageViewSet

# 创建主路由
router = DefaultRouter()
router.register(r'', ShelterViewSet, basename='shelter')

# 创建独立的工作人员路由
staff_router = DefaultRouter()
staff_router.register(r'', ShelterStaffViewSet, basename='shelter-staff')

donations_router = DefaultRouter()
donations_router.register(r'', DonationViewSet, basename='donation')

interactions_router = DefaultRouter()
interactions_router.register(r'', InteractionApplicationViewSet, basename='interaction-application')

activities_router = DefaultRouter()
activities_router.register(r'', ShelterActivityViewSet, basename='shelter-activity')

usages_router = DefaultRouter()
usages_router.register(r'', DonationUsageViewSet, basename='donation-usage')

urlpatterns = [
    path('', include(router.urls)),
    path('staff/', include(staff_router.urls)),  # 独立的工作人员路由
    path('<int:shelter_pk>/staff/', include(staff_router.urls)),
    path('<int:shelter_pk>/donations/', include(donations_router.urls)),
    path('<int:shelter_pk>/interactions/', include(interactions_router.urls)),
    path('<int:shelter_pk>/activities/', include(activities_router.urls)),
    path('<int:shelter_pk>/usages/', include(usages_router.urls)),
]
