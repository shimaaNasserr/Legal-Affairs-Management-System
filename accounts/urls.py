from django.urls import path
from .views import RoleListView, RegisterView, LoginView, UserDetailView, InviteSecretaryView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("invite-secretary/", InviteSecretaryView.as_view(), name="invite-secretary"),
    path("roles/", RoleListView.as_view(), name="roles-list"),

]

