from django.urls import path
from .views import (
    CourtListCreateAPIView,
    CourtRetrieveUpdateDestroyAPIView,
    CourtDivisionByCourtAPIView,
)

urlpatterns = [
    path("", CourtListCreateAPIView.as_view(), name="courts-list"),
    path("<uuid:pk>/", CourtRetrieveUpdateDestroyAPIView.as_view(), name="court-detail"),
    path("<uuid:court_id>/divisions/", CourtDivisionByCourtAPIView.as_view(), name="court-divisions"),
]
