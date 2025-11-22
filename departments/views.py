from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import Department
from accounts.serializers import DepartmentSerializer


class DepartmentListView(generics.ListAPIView):
    """
    قائمة بجميع الإدارات
    متاح لجميع المستخدمين المسجلين
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class DepartmentDetailView(generics.RetrieveAPIView):
    """
    تفاصيل إدارة محددة
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
