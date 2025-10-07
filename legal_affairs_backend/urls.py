from django.contrib import admin
from django.urls import path , include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls")),
    path('api/', include('fatwas.urls')),
    path('api/cases/', include('cases.urls')), 

    path("api/contracts/", include("contracts.urls")),
]
