from rest_framework import viewsets, filters, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Fatwa
from .serializers import FatwaSerializer
from .permissions import FatwaPermission

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class FatwaViewSet(viewsets.ModelViewSet):
    queryset = Fatwa.objects.select_related('department', 'created_by').all().order_by('-created_at')
    serializer_class = FatwaSerializer
    permission_classes = [FatwaPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['general_number']
    ordering_fields = ['created_at']
    pagination_class = StandardResultsSetPagination

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

    # Basic error-handling wrappers to return consistent responses
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
