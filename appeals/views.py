# appeals/views.py
from rest_framework import viewsets, filters, status,permissions
from rest_framework.permissions import AllowAny
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from investigations.models import Appeal
from .serializers import AppealSerializer
from .permissions import IsAppealAllowed

class AppealViewSet(viewsets.ModelViewSet):
    queryset = Appeal.objects.select_related(
        "investigation", "department", "complainant", "created_by", "reviewed_by"
    ).all()
    serializer_class = AppealSerializer
    permission_classes = [IsAppealAllowed]

    def get_permissions(self):
        # Development-only: disable auth for appeal CRUD to aid local testing
        if getattr(settings, "DEBUG", False):
            return [AllowAny()]
        return super().get_permissions()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["investigation", "complainant", "department", "status"]
    search_fields = ["appeal_number", "appellant_name", "appeal_reason"]
    ordering_fields = ["created_at", "date_submitted", "appeal_number"]
    ordering = ['-created_at']

    def get_queryset(self):
        """تخصيص الكويريست بناءً على الصلاحيات"""
        if getattr(settings, "DEBUG", False):
            return super().get_queryset()
        queryset = super().get_queryset()
        user = self.request.user
        print(f"=== DEBUG: User {getattr(user, 'username', 'anon')} requesting appeals ===")
        return queryset

    def perform_create(self, serializer):
        """تعيين المنشئ والمشتكي تلقائياً"""
        print(f"=== DEBUG: Creating appeal for user {self.request.user.username} ===")
        serializer.save(
            created_by=self.request.user,
            complainant=self.request.user
        )

    def create(self, request, *args, **kwargs):
        """تجاوز دالة الإنشاء لضمان إرجاع البيانات بشكل صحيح"""
        print("=== DEBUG: Create method called ===")
        
        # Debug the incoming data
        print(f"Request data: {request.data}")
        print(f"User: {request.user.username}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            print(f"=== DEBUG: Appeal created successfully ===")
            print(f"Created appeal data: {serializer.data}")
            
            # Return the created object with proper response
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
        except Exception as e:
            print(f"=== DEBUG: Error creating appeal: {str(e)} ===")
            return Response(
                {"detail": f"Error creating appeal: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        """تجاوز دالة العرض لفحص البيانات"""
        print("=== DEBUG: List method called ===")
        
        queryset = self.filter_queryset(self.get_queryset())
        print(f"Queryset count: {queryset.count()}")
        
        # Debug: Print all appeals in the queryset
        for appeal in queryset:
            print(f"Appeal: {appeal.appeal_number} - {appeal.appellant_name} - Created by: {appeal.created_by.username}")
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            print(f"Paginated data count: {len(serializer.data)}")
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        print(f"Serialized data count: {len(serializer.data)}")
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """التحقق من إمكانية الحذف قبل التنفيذ"""
        obj = self.get_object()
        if not obj.can_be_deleted():
            return Response(
                {"detail": "Cannot delete appeal linked to a closed investigation."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="my")
    def my_appeals(self, request):
        """الاستئنافات الخاصة بالمستخدم الحالي"""
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication required."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print(f"=== DEBUG: My appeals for user {user.username} ===")
        
        # استئنافات المستخدم كمشتكي
        user_appeals = self.get_queryset().filter(complainant=user)
        print(f"Found {user_appeals.count()} appeals for complainant {user.username}")
        
        page = self.paginate_queryset(user_appeals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(user_appeals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="debug")
    def debug_info(self, request):
        """معلومات تصحيح للأخطاء"""
        user = request.user
        
        data = {
            "user_info": {
                "username": user.username,
                "id": user.id,
                "role": getattr(user, 'role', 'No role'),
                "is_authenticated": user.is_authenticated,
            },
            "appeals_info": {
                "total_in_db": Appeal.objects.count(),
                "user_as_complainant": Appeal.objects.filter(complainant=user).count(),
                "user_as_creator": Appeal.objects.filter(created_by=user).count(),
                "all_appeals": list(Appeal.objects.values('id', 'appeal_number', 'appellant_name', 'complainant_id', 'created_by_id'))
            },
            "queryset_info": {
                "filtered_count": self.get_queryset().count(),
                "queryset_details": [
                    {
                        'id': str(appeal.id),
                        'appeal_number': appeal.appeal_number,
                        'appellant_name': appeal.appellant_name,
                        'complainant': appeal.complainant.username if appeal.complainant else 'None',
                        'created_by': appeal.created_by.username if appeal.created_by else 'None',
                        'department': appeal.department.name if appeal.department else 'None'
                    }
                    for appeal in self.get_queryset()
                ]
            }
        }
        
        return Response(data)
