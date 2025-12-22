from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleListView, 
    RegisterView, 
    LoginView,  
    InviteSecretaryView,
    UserViewSet ,
    RequestPasswordReset, PasswordResetConfirm, GoogleAuthView

)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("invite-secretary/", InviteSecretaryView.as_view(), name="invite-secretary"),
    path("roles/", RoleListView.as_view(), name="roles-list"),
    path("", include(router.urls)),  # يتضمن /api/accounts/users/ ,
    path('password/reset/', RequestPasswordReset.as_view()),
    path('password/reset/confirm/', PasswordResetConfirm.as_view()),
    path('google/', GoogleAuthView.as_view()),

]

