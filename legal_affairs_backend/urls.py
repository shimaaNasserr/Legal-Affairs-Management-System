from django.contrib import admin
from django.urls import path , include
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from appeals.views import AppealViewSet

router = DefaultRouter()
router.register(r'appeals', AppealViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path('api/', include('fatwas.urls')),
    path('api/cases/', include('cases.urls')), 
    path('api/', include('investigations.urls')),
    path("api/", include("appeals.urls")),
    path("api/courts/", include("courts.urls")),

    path("api/contracts/", include("contracts.urls")),
]
