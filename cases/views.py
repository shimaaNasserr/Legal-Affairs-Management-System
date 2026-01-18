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

        if user.role_name in ["GeneralManager", "President"]:
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
                return qs
            return Case.objects.none()
        if user.role_name == "Lawyer":
            if user.department and user.department.name == "إدارة القضايا":
                return qs.filter(created_by=user)
            return Case.objects.none()
        if user.role_name == "Secretary" and user.assigned_lawyer:
            # Secretary can see cases created by their assigned lawyer
            return qs.filter(created_by=user.assigned_lawyer)
        return Case.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        print(f"DEBUG: Trying to create case with user: {user.username}")
        print(f"DEBUG: User role: {user.role_name}")
        print(f"DEBUG: User department: {getattr(user.department, 'name', None) if user.department else None}")
        print(f"DEBUG: Has assigned lawyer: {user.assigned_lawyer is not None}")
        if user.assigned_lawyer:
            print(f"DEBUG: Assigned lawyer: {user.assigned_lawyer.username}")
            print(f"DEBUG: Assigned lawyer department: {getattr(user.assigned_lawyer.department, 'name', None) if user.assigned_lawyer.department else None}")
        
        if user.role_name in ["GeneralManager", "President", "DepartmentManager"] and (user.role_name not in ["DepartmentManager"] or (user.department and user.department.name == "إدارة القضايا")):
            print("DEBUG: GeneralManager/President/DepartmentManager path")
            serializer.save(created_by=user)
        elif user.role_name == "Lawyer" and user.department and user.department.name == "إدارة القضايا":
            print("DEBUG: Lawyer path")
            serializer.save(created_by=user)
        elif user.role_name == "Secretary" and user.assigned_lawyer:
            print("DEBUG: Secretary path")
            # Secretary creates case on behalf of their assigned lawyer
            serializer.save(created_by=user.assigned_lawyer)
        else:
            print("DEBUG: Permission denied path")
            raise PermissionDenied("ليس لديك صلاحية إضافة قضية")

    def perform_update(self, serializer):
        user = self.request.user
        case = self.get_object()
        if user.role_name in ["GeneralManager", "President", "DepartmentManager"] and (user.role_name not in ["DepartmentManager"] or (user.department and user.department.name == "إدارة القضايا")):
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
        if user.role_name in ["GeneralManager", "President", "DepartmentManager"] and (user.role_name not in ["DepartmentManager"] or (user.department and user.department.name == "إدارة القضايا")):
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
