from django.urls import path
from .views import DepartmentListView, DepartmentDetailView

urlpatterns = [
    path("", DepartmentListView.as_view(), name="departments-list"),
    path("<uuid:pk>/", DepartmentDetailView.as_view(), name="department-detail"),
]

