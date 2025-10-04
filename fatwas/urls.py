from rest_framework.routers import DefaultRouter
from .views import FatwaViewSet

router = DefaultRouter()
router.register(r'fatwas', FatwaViewSet, basename='fatwas')

urlpatterns = router.urls
