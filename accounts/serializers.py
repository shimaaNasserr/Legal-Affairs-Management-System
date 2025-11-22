from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from accounts.models import Role , Department

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    department_id = serializers.UUIDField(source="department.id", read_only=True)
    assigned_lawyer_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", 
            "username", 
            "email", 
            "first_name", 
            "last_name", 
            "role",
            "department",
            "department_name",
            "department_id",
            "assigned_lawyer",
            "assigned_lawyer_name"
        ]
        read_only_fields = ["id", "email"]

    def get_assigned_lawyer_name(self, obj):
        """إرجاع اسم المحامي المسؤول"""
        if obj.assigned_lawyer:
            return f"{obj.assigned_lawyer.first_name} {obj.assigned_lawyer.last_name}"
        return None


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
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        required=False,
        allow_null=True,
        write_only=True
    )
    department_name = serializers.CharField(source="department.name", read_only=True)
    assigned_lawyer_name = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "id", 
            "username", 
            "email", 
            "first_name", 
            "last_name", 
            "role",
            "role_id",
            "department", 
            "department_name",
            "assigned_lawyer",
            "assigned_lawyer_name",
            "password"
        ]
        read_only_fields = ["id"]

    def get_assigned_lawyer_name(self, obj):
        """إرجاع اسم المحامي المسؤول"""
        if obj.assigned_lawyer:
            return f"{obj.assigned_lawyer.first_name} {obj.assigned_lawyer.last_name}"
        return None

    def create(self, validated_data):
        """إنشاء مستخدم جديد مع كلمة مرور"""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """تحديث مستخدم مع كلمة مرور اختيارية"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def get_fields(self):
        fields = super().get_fields()
        if 'request' in self.context:
            request_user = self.context['request'].user

            # التحقق من وجود role قبل الوصول إلى name
            role_name = request_user.role_name
            if not request_user.is_superuser and role_name and role_name.lower() != "president":
                # المستخدم العادي لا يستطيع تعديل الدور، الإدارة، assigned_lawyer
                for field in ["role", "role_id", "department", "assigned_lawyer", "email"]:
                    if field in fields:
                        fields[field].read_only = True

        return fields
