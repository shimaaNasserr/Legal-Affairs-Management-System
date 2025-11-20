from rest_framework import viewsets, filters, permissions
from .models import Fatwa
from .serializers import FatwaSerializer
from .permissions import FatwaPermission

class FatwaViewSet(viewsets.ModelViewSet):
    queryset = Fatwa.objects.select_related('department', 'created_by').all().order_by('-created_at')
    serializer_class = FatwaSerializer
    permission_classes = [FatwaPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['general_number']
    ordering_fields = ['created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # فلترة حسب التاريخ أو رقم الحصر
        date = self.request.query_params.get('date')
        general_number = self.request.query_params.get('general_number')

        if date:
            queryset = queryset.filter(created_at__date=date)
        if general_number:
            queryset = queryset.filter(general_number=general_number)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
