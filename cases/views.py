from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import PermissionDenied

from .models import Case, LawyerSecretaryAccess
from .serializers import CaseSerializer, LawyerSecretaryAccessSerializer
from .permissions import CasePermissions

class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all().select_related('department', 'created_by').prefetch_related('lawyers')
    serializer_class = CaseSerializer
    permission_classes = [CasePermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['department', 'case_status', 'appeal_status']
    search_fields = ['case_number', 'lawsuit_number', 'plaintiff', 'defendant', 'court']

    def get_queryset(self):
        return Case.objects.all().select_related('department', 'created_by').prefetch_related('lawyers')


    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user)

    @action(detail=False, methods=['get'], url_path='my-cases')
    def my_cases(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(case_status='pending').count(),
            'under_study': queryset.filter(case_status='under_study').count(),
            'in_court': queryset.filter(case_status='in_court').count(),
            'closed': queryset.filter(case_status='closed').count(),
            'appealed': queryset.filter(appeal_status=True).count(),
        }
        return Response(stats)

class LawyerSecretaryAccessViewSet(viewsets.ModelViewSet):
    queryset = LawyerSecretaryAccess.objects.select_related('lawyer', 'secretary')
    serializer_class = LawyerSecretaryAccessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role_name == "GeneralManager":
            return Case.objects.all()

        # رئيس الجامعة يشوف كل القضايا (read only)
        if user.role_name == "President":
            return Case.objects.all()

        # المحامي يشوف قضاياه فقط
        if user.role_name == "Lawyer":
            return Case.objects.filter(created_by=user)

        # لو داخل قسم القضايا (غير محامي / مدير)
        if hasattr(user, "department") and user.department and user.department.name == "إدارة القضايا ":
            return Case.objects.all()

        # أي حد تاني → لا يشوف شيء
        return Case.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role_name == 'Lawyer':
            serializer.save(lawyer=user)
        elif user.role_name in ['President', 'GeneralManager']:
            serializer.save()
        else:
            raise PermissionDenied("لا تملك صلاحية إنشاء هذا الربط")
