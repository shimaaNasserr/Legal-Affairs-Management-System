from rest_framework import viewsets, filters, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Fatwa
from .serializers import FatwaSerializer
from .permissions import FatwaPermission

class FatwaViewSet(viewsets.ModelViewSet):
    queryset = Fatwa.objects.select_related('department', 'created_by').all().order_by('-created_at')
    serializer_class = FatwaSerializer
    permission_classes = [permissions.IsAuthenticated, FatwaPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['general_number']
    ordering_fields = ['created_at']
    
    class TenSizePagination(PageNumberPagination):
        page_size = 10
        page_size_query_param = "page_size"
        max_page_size = 100

    pagination_class = TenSizePagination

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        role_name = (getattr(user, "role_name", None) or "").lower()

        # Non-admin roles only see their own department's records
        if role_name not in {"president", "general_manager"}:
            user_dept_id = getattr(getattr(user, "department", None), "id", None)
            queryset = queryset.filter(department_id=user_dept_id)

        # فلترة حسب التاريخ أو رقم الحصر
        date = self.request.query_params.get('date')
        general_number = self.request.query_params.get('general_number')

        if date:
            queryset = queryset.filter(created_at__date=date)
        if general_number:
            queryset = queryset.filter(general_number=general_number)
        return queryset

    def perform_create(self, serializer):
        # Ensure created_by is set; only force department for non-admin roles
        user = self.request.user
        role_name = (getattr(user, "role_name", None) or "").lower()
        save_kwargs = {"created_by": user}

        # Non-admin roles cannot choose department; bind to user's department
        if role_name not in {"president", "general_manager"}:
            save_kwargs["department"] = getattr(user, "department", None)

        serializer.save(**save_kwargs)
