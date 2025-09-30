from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from rest_framework.views import APIView
from .permissions import IsLawyer
from .models import Role
from .serializers import RoleSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.models import Role, Department
from django.shortcuts import get_object_or_404
from accounts.models import User
from .serializers import UserDetailSerializer


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(email=email, password=password)

        if user is None:
            return Response(
                {"detail": "البريد الإلكتروني أو كلمة المرور غير صحيحة."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "تسجيل الدخول ناجح",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data
        })


class UserDetailSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "department", "assigned_lawyer"]

    def get_fields(self):
        fields = super().get_fields()
        request_user = self.context['request'].user

        if not request_user.is_superuser and request_user.role.name != "president":
            # المستخدم العادي لا يستطيع تعديل الدور، الإدارة، assigned_lawyer
            for field in ["role", "department", "assigned_lawyer", "email"]:
                fields[field].read_only = True

        return fields




class InviteSecretaryView(APIView):
    permission_classes = [IsAuthenticated, IsLawyer]

    def post(self, request):
        email = request.data.get("email")
        try:
            secretary = User.objects.get(email=email)
            secretary.assigned_lawyer = request.user
            secretary.save()
            return Response({"message": "تم ربط السكرتير بالمحامي بنجاح"})
        except User.DoesNotExist:
            return Response({"detail": "لا يوجد مستخدم بهذا البريد"}, status=404)
        


class RoleListView(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = get_object_or_404(User, pk=self.kwargs["pk"])
        request_user = self.request.user
        user_role = getattr(request_user.role, "name", None)

        # المحامي: فقط السكرتاريه المرتبطين به
        if user_role == "lawyer":
            if obj.assigned_lawyer != request_user:
                from rest_framework.exceptions import PermissionDenied
                if self.request.method in ["PUT", "PATCH"]:
                    raise PermissionDenied("ليس لديك صلاحية تعديل هذا المستخدم.")
        
        # المستخدم العادي: فقط نفسه يمكنه التعديل
        elif obj != request_user and not request_user.is_superuser and user_role != "president":
            if self.request.method in ["PUT", "PATCH"]:
                raise PermissionDenied("يمكنك تعديل بياناتك فقط.")

        return obj


