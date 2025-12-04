from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.db.models import Q

from .models import Contract
from .serializers import ContractSerializer
from .permissions import ContractPermissions


class TenSizePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, ContractPermissions]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = TenSizePagination

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        role = getattr(getattr(user, "role", None), "name", None)
        role_l = (role or "").lower()

        # Visibility restrictions by department for non-admin roles
        if role_l not in {"president", "general_manager"}:
            user_dept_id = getattr(getattr(user, "department", None), "id", None)
            qs = qs.filter(department_id=user_dept_id)

        # Filters
        contract_type = self.request.query_params.get("contract_type")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        general_number = self.request.query_params.get("general_number")
        expiry = (self.request.query_params.get("expiry") or "").lower()

        if contract_type:
            qs = qs.filter(contract_type=contract_type)
        if general_number:
            qs = qs.filter(general_number__icontains=general_number)
        if date_from:
            qs = qs.filter(date_received__gte=date_from)
        if date_to:
            qs = qs.filter(date_received__lte=date_to)

        # Expiry filters
        if expiry in {"expired", "expiring"}:
            today = timezone.localdate()
            if expiry == "expired":
                qs = qs.filter(end_date__lt=today)
            else:  # expiring within next 60 days (including today)
                in_60 = today + timezone.timedelta(days=60)
                qs = qs.filter(end_date__gte=today, end_date__lte=in_60)
                qs = qs.order_by("end_date")

        return qs

    def perform_create(self, serializer):
        # Ensure created_by and default department set from user if not provided
        user = self.request.user
        department = getattr(user, "department", None)
        serializer.save(created_by=user, department=department)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx
