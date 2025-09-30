from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from accounts.models import Role , Department

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def validate_email(self, value):
        """تأكد أن الإيميل غير مستخدم مسبقًا."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get("username", ""),
            email=validated_data["email"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password=validated_data["password"]
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
        data["user"] = user
        return data


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description"]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code"]



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
