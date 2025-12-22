# views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Case
from .serializers import CaseSerializer
from .permissions import CasePermissions

class CaseViewSet(viewsets.ModelViewSet):
    serializer_class = CaseSerializer
    permission_classes = [CasePermissions]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['department', 'case_status', 'appeal_status']
    search_fields = ['case_number', 'lawsuit_number', 'plaintiff', 'defendant', 'court__name']

    def get_queryset(self):
        user = self.request.user

        qs = (
            Case.objects
            .select_related(
                'department',
                'created_by',
                'court',
                'division'
            )
            .prefetch_related('lawyers')
        )

        if user.role_name == "GeneralManager":
            return qs

        if user.role_name == "DepartmentManager":
            if user.department and user.department.name == "إدارة القضايا":
                return qs
            return Case.objects.none()

        if user.role_name == "President":
            return qs

        if user.role_name == "Lawyer":
            if user.department and user.department.name == "إدارة القضايا":
                return qs.filter(created_by=user)
            return Case.objects.none()

        return Case.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        print(f"Trying to create case with user: {user.username} - {user.role_name} {getattr(user.department, 'name', None)}")  # debug
        if user.role_name in ["GeneralManager", "DepartmentManager"] and (user.role_name != "DepartmentManager" or (user.department and user.department.name == "إدارة القضايا")):
            serializer.save(created_by=user)
        elif user.role_name == "Lawyer" and user.department and user.department.name == "إدارة القضايا":
            serializer.save(created_by=user)
        else:
            raise PermissionDenied("ليس لديك صلاحية إضافة قضية")

    def perform_update(self, serializer):
        user = self.request.user
        case = self.get_object()
        if user.role_name in ["GeneralManager", "DepartmentManager"] and (user.role_name != "DepartmentManager" or (user.department and user.department.name == "إدارة القضايا")):
            serializer.save()
        elif user.role_name == "Lawyer" and case.created_by == user:
            serializer.save()
        else:
            raise PermissionDenied("ليس لديك صلاحية تعديل هذه القضية")

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role_name in ["GeneralManager", "DepartmentManager"] and (user.role_name != "DepartmentManager" or (user.department and user.department.name == "إدارة القضايا")):
            instance.delete()
        else:
            raise PermissionDenied("ليس لديك صلاحية حذف هذه القضية")

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
