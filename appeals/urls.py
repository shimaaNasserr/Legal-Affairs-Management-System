from rest_framework.routers import DefaultRouter
from .views import AppealViewSet

router = DefaultRouter()
router.register(r"appeals", AppealViewSet, basename="appeal")

urlpatterns = router.urls
