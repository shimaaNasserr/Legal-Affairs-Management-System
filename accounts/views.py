from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from rest_framework.views import APIView
from .permissions import IsLawyer, IsPresident, IsGeneralManager
from .models import Role
from .serializers import RoleSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.models import Role, Department
from django.shortcuts import get_object_or_404
from accounts.models import User
from .serializers import UserDetailSerializer
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import permissions

from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetToken
from rest_framework.exceptions import AuthenticationFailed
from google.oauth2 import id_token
from google.auth.transport import requests


User = get_user_model()

class IsPresidentOrGeneralManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return IsPresident().has_permission(request, view) or IsGeneralManager().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        return IsPresident().has_object_permission(request, view, obj) or IsGeneralManager().has_object_permission(request, view, obj)

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

        # التحقق من وجود role قبل الوصول إلى name
        role_name = request_user.role_name
        if not request_user.is_superuser and role_name and role_name.lower() != "president":
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
        # توحيد الأسماء - مقارنة case-insensitive
        if user_role and user_role.lower() == "lawyer":
            if obj.assigned_lawyer != request_user:
                from rest_framework.exceptions import PermissionDenied
                if self.request.method in ["PUT", "PATCH"]:
                    raise PermissionDenied("ليس لديك صلاحية تعديل هذا المستخدم.")
        
        # المستخدم العادي: فقط نفسه يمكنه التعديل
        elif obj != request_user and not request_user.is_superuser and (not user_role or user_role.lower() != "president"):
            if self.request.method in ["PUT", "PATCH"]:
                raise PermissionDenied("يمكنك تعديل بياناتك فقط.")

        return obj


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet لإدارة المستخدمين
    فقط الرئيس ومدير العام يمكنهم الوصول
    """
    queryset = User.objects.all().select_related('role', 'department', 'assigned_lawyer')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['role', 'department']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_serializer_class(self):
        """اختيار Serializer حسب العملية"""
        if self.action in ['create', 'update', 'partial_update']:
            return UserDetailSerializer
        return UserSerializer

    def get_queryset(self):
        """تخصيص QuerySet حسب دور المستخدم"""
        user = self.request.user
        role_name = user.role_name

        # الرئيس ومدير العام: جميع المستخدمين
        if role_name in ['President', 'GeneralManager']:
            # فلترة حسب الدور إذا تم تمرير role في query params
            role_filter = self.request.query_params.get('role', None)
            if role_filter:
                return User.objects.filter(role__name=role_filter).select_related('role', 'department', 'assigned_lawyer')
            return User.objects.all().select_related('role', 'department', 'assigned_lawyer')

        # باقي المستخدمين: لا يمكنهم الوصول
        return User.objects.none()

    def get_permissions(self):
        """تحديد الصلاحيات حسب العملية"""
        if self.action in ['list', 'retrieve']:
            # فقط الرئيس ومدير العام يمكنهم عرض المستخدمين
            return [IsAuthenticated(), IsPresidentOrGeneralManager()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # فقط الرئيس يمكنه إنشاء/تعديل/حذف المستخدمين
            return [IsAuthenticated(), IsPresident()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """إنشاء مستخدم جديد"""
        user = self.request.user
        if user.role_name != 'President':
            raise PermissionDenied("فقط الرئيس يمكنه إنشاء مستخدمين جدد")
        serializer.save()

    def perform_update(self, serializer):
        """تحديث مستخدم"""
        user = self.request.user
        if user.role_name != 'President':
            raise PermissionDenied("فقط الرئيس يمكنه تعديل المستخدمين")
        serializer.save()

    def perform_destroy(self, instance):
        """حذف مستخدم"""
        user = self.request.user
        if user.role_name != 'President':
            raise PermissionDenied("فقط الرئيس يمكنه حذف المستخدمين")
        # منع حذف المستخدم الحالي
        if instance == user:
            raise PermissionDenied("لا يمكنك حذف نفسك")
        instance.delete()




class RequestPasswordReset(APIView):
    permission_classes = []  

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"message": "يرجى إدخال البريد الإلكتروني"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "البريد غير مسجل"}, status=404)

        # إنشاء توكن جديد
        reset_token = PasswordResetToken.objects.create(user=user)

        reset_link = f"http://localhost:5173/reset-password/{reset_token.token}"

        # إرسال الإيميل
        try:
            send_mail(
                subject="إعادة تعيين كلمة المرور",
                message=f"اضغط على الرابط التالي لإعادة تعيين كلمة المرور:\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"message": "حدث خطأ أثناء إرسال الإيميل", "error": str(e)}, status=500)

        return Response({"message": "تم إرسال رابط إعادة تعيين كلمة المرور للإيميل"})
    


class PasswordResetConfirm(APIView):

    permission_classes = []  
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("password")

        try:
            token_obj = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"message": "الرابط غير صالح"}, status=400)
        

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        # حذف التوكن بعد الاستخدام
        token_obj.delete()

        return Response({"message": "تم تغيير كلمة المرور بنجاح"})



class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get("credential")

        try:
            google_user = id_token.verify_oauth2_token(token, requests.Request())
        except Exception:
            raise AuthenticationFailed("Token invalid")

        email = google_user["email"]
        name = google_user.get("name", "")

        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "first_name": name}
        )

        # You can generate a JWT token here if needed
        return Response({
            "message": "logged in",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.first_name
            }
        })
