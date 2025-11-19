from django.contrib import admin
from django.urls import path , include
from .views import ReportsSummaryView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path('api/', include('fatwas.urls')),
    path('api/cases/', include('cases.urls')), 
    path('api/', include('investigations.urls')),

    path("api/contracts/", include("contracts.urls")),
    path("api/reports/summary/", ReportsSummaryView.as_view()),
]
