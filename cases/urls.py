from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CaseViewSet, LawyerSecretaryAccessViewSet

router = DefaultRouter()
router.register(r'', CaseViewSet, basename='case')
router.register(r'secretary-access', LawyerSecretaryAccessViewSet, basename='lawyer-secretary-access')

urlpatterns = [
    path('', include(router.urls)),
]