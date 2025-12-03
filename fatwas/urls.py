from rest_framework.routers import DefaultRouter
from .views import FatwaViewSet

router = DefaultRouter()
router.register(r'fatwas', FatwaViewSet, basename='fatwas')
from django.urls import path, include

urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns = router.urls
