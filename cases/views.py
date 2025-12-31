# views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from .models import Case
from .serializers import CaseSerializer
from .permissions import CasePermissions

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 100

class CaseViewSet(viewsets.ModelViewSet):
    serializer_class = CaseSerializer
    permission_classes = [CasePermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    # Add date filtering support and keep existing filters
    filterset_fields = ['department', 'case_status', 'appeal_status', 'date_received']
    # Search covers name fields so UI can search by name
    search_fields = ['case_number', 'lawsuit_number', 'plaintiff', 'defendant', 'court__name']

    def get_queryset(self):
        user = self.request.user
        qs = Case.objects.select_related('department', 'created_by').prefetch_related('lawyers')

        role = getattr(user, 'role_name', None)
        # President and GeneralManager: full access
        if role in ["President", "GeneralManager"]:
            pass
        # Secretary: full access including data entry
        if role == "Secretary" or (role and role.lower() == "secretary"):
            return qs
        # DepartmentManager: only own department
        if role == "DepartmentManager" or (role and role.lower() == "department_manager"):
            if user.department:
                qs = qs.filter(department=user.department)
            else:
                return Case.objects.none()
        # Lawyer: only cases created by the lawyer within cases department
        if role == "Lawyer" or (role and role.lower() == "lawyer"):
            if user.department and user.department.name == "إدارة القضايا":
                qs = qs.filter(created_by=user)
            else:
                return Case.objects.none()
        # Apply date range filters
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date_received__gte=date_from)
        if date_to:
            qs = qs.filter(date_received__lte=date_to)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, 'role_name', None)
        if role in ["President", "GeneralManager"]:
            serializer.save(created_by=user)
            return
        if role == "Secretary" or (role and role.lower() == "secretary"):
            serializer.save(created_by=user)
            return
        if role == "DepartmentManager" or (role and role.lower() == "department_manager"):
            if user.department:
                serializer.save(created_by=user, department=user.department)
                return
        if role == "Lawyer" or (role and role.lower() == "lawyer"):
            if user.department and user.department.name == "إدارة القضايا":
                serializer.save(created_by=user)
                return
        raise PermissionDenied("ليس لديك صلاحية إضافة قضية")

    def perform_update(self, serializer):
        user = self.request.user
        case = self.get_object()
        role = getattr(user, 'role_name', None)
        if role in ["President", "GeneralManager"]:
            serializer.save()
            return
        if role == "Secretary" or (role and role.lower() == "secretary"):
            serializer.save()
            return
        if role == "DepartmentManager" or (role and role.lower() == "department_manager"):
            if user.department and case.department_id == user.department_id:
                serializer.save()
                return
        if role == "Lawyer" or (role and role.lower() == "lawyer"):
            if case.created_by_id == user.id:
                serializer.save()
                return
        raise PermissionDenied("ليس لديك صلاحية تعديل هذه القضية")

    def perform_destroy(self, instance):
        user = self.request.user
        role = getattr(user, 'role_name', None)
        if role in ["President", "GeneralManager"]:
            instance.delete()
            return
        if role == "Secretary" or (role and role.lower() == "secretary"):
            instance.delete()
            return
        if role == "DepartmentManager" or (role and role.lower() == "department_manager"):
            if user.department and instance.department_id == user.department_id:
                instance.delete()
                return
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
