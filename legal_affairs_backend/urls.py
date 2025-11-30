from django.contrib import admin
from django.urls import path , include

from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from appeals.views import AppealViewSet
from .views import ReportsSummaryView


router = DefaultRouter()
router.register(r'appeals', AppealViewSet)

# تحسين عناوين لوحة الإدارة بالعربية - جامعة بورسعيد
admin.site.site_header = "نظام إدارة الشئون القانونية - جامعة بورسعيد"
admin.site.site_title = "إدارة الشئون القانونية - جامعة بورسعيد"
admin.site.index_title = "مرحباً بك في لوحة التحكم - جامعة بورسعيد"

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include(router.urls)),
    path("api/accounts/", include("accounts.urls")),
    path('api/', include('fatwas.urls')),
    path('api/cases/', include('cases.urls')), 
    path('api/', include('investigations.urls')),
    path("api/", include("appeals.urls")),
    path("api/courts/", include("courts.urls")),
    path("api/departments/", include("departments.urls")),
    path("api/contracts/", include("contracts.urls")),
    path("api/reports/summary/", ReportsSummaryView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
