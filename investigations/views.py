from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Investigation, Appeal
from .serializers import (
    InvestigationSerializer, 
    AppealSerializer, 
    InvestigationStatsSerializer,
    InvestigationSummarySerializer
)
from .permissions import InvestigationPermissions, AppealPermissions, InvestigationViewPermissions


class InvestigationViewSet(viewsets.ModelViewSet):
    """ViewSet للتحقيقات مع جميع العمليات CRUD والإحصائيات"""
    
    queryset = Investigation.objects.all().select_related(
        'department', 'created_by'
    ).prefetch_related('assigned_investigators', 'appeals')
    
    serializer_class = InvestigationSerializer
    permission_classes = [InvestigationPermissions, InvestigationViewPermissions]
    
    # فلاتر البحث والترتيب
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['department', 'status', 'priority', 'case_type', 'complainant_type', 'faculty_college', 'created_by']
    search_fields = ['title', 'description', 'accused_names', 'general_number', 'complainant_name', 'faculty_college']
    ordering_fields = ['created_at', 'date_received', 'date_started', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """تخصيص QuerySet حسب دور المستخدم"""
        user = self.request.user
        
        role_name = user.role_name
        if not role_name:
            return Investigation.objects.none()
        
        # President و GeneralManager: جميع التحقيقات
        if role_name in ['President', 'GeneralManager']:
            return Investigation.objects.all()
        
        # DepartmentManager: تحقيقات إدارته فقط
        if role_name == 'DepartmentManager':
            return Investigation.objects.filter(department=user.department)
        
        # Lawyer: التحقيقات المعينة له أو من إدارته
        if role_name == 'Lawyer':
            return Investigation.objects.filter(
                Q(assigned_investigators=user) | 
                Q(department=user.department)
            ).distinct()
        
        # Secretary: التحقيقات المرتبطة بالمحامي المسؤول
        if role_name == 'Secretary':
            if user.assigned_lawyer:
                return Investigation.objects.filter(
                    assigned_investigators=user.assigned_lawyer
                ).distinct()
            return Investigation.objects.none()
        
        return Investigation.objects.none()
    
    def get_serializer_class(self):
        """اختيار Serializer حسب العملية"""
        if self.action == 'list':
            return InvestigationSummarySerializer
        return InvestigationSerializer
    
    def perform_create(self, serializer):
        """إنشاء تحقيق جديد مع تعيين المنشئ"""
        user = self.request.user
        
        # تعيين المنشئ
        investigation = serializer.save(created_by=user)
        
        # إذا كان المستخدم محامي، تعيينه كمحقق تلقائياً
        if user.role_name == 'Lawyer':
            investigation.assigned_investigators.add(user)
        
        # تعيين الإدارة إذا لم تُحدد
        if not investigation.department and user.department:
            investigation.department = user.department
            investigation.save()
    
    @action(detail=False, methods=['get'], url_path='my-investigations')
    def my_investigations(self, request):
        """التحقيقات الخاصة بالمستخدم الحالي"""
        user = request.user
        role_name = user.role_name
        
        if role_name == 'Lawyer':
            queryset = Investigation.objects.filter(assigned_investigators=user)
        elif role_name == 'Secretary' and user.assigned_lawyer:
            queryset = Investigation.objects.filter(assigned_investigators=user.assigned_lawyer)
        else:
            queryset = Investigation.objects.filter(created_by=user)
        
        serializer = InvestigationSummarySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """إحصائيات التحقيقات"""
        queryset = self.get_queryset()
        
        # إحصائيات عامة
        total = queryset.count()
        pending = queryset.filter(status='pending').count()
        under_investigation = queryset.filter(status='under_investigation').count()
        completed = queryset.filter(status='completed').count()
        closed = queryset.filter(status='closed').count()
        appealed = queryset.filter(status='appealed').count()
        
        # إحصائيات حسب الأولوية
        low_priority = queryset.filter(priority='low').count()
        medium_priority = queryset.filter(priority='medium').count()
        high_priority = queryset.filter(priority='high').count()
        urgent_priority = queryset.filter(priority='urgent').count()
        
        # إحصائيات زمنية
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        this_month = queryset.filter(created_at__gte=this_month_start).count()
        last_month = queryset.filter(
            created_at__gte=last_month_start,
            created_at__lt=this_month_start
        ).count()
        
        stats_data = {
            'total': total,
            'pending': pending,
            'under_investigation': under_investigation,
            'completed': completed,
            'closed': closed,
            'appealed': appealed,
            'low_priority': low_priority,
            'medium_priority': medium_priority,
            'high_priority': high_priority,
            'urgent_priority': urgent_priority,
            'this_month': this_month,
            'last_month': last_month,
        }
        
        serializer = InvestigationStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign_investigator(self, request, pk=None):
        """تعيين محقق للتحقيق"""
        investigation = self.get_object()
        investigator_id = request.data.get('investigator_id')
        
        if not investigator_id:
            return Response(
                {'error': 'معرف المحقق مطلوب'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from accounts.models import User
            investigator = User.objects.get(id=investigator_id)
            
            # التحقق من أن المستخدم محامي أو له دور مناسب
            investigator_role = investigator.role_name
            if not investigator_role or investigator_role not in ['Lawyer', 'DepartmentManager']:
                return Response(
                    {'error': 'المستخدم المحدد لا يمكنه أن يكون محققاً'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            investigation.assigned_investigators.add(investigator)
            
            return Response({
                'message': f'تم تعيين {investigator.username} كمحقق بنجاح',
                'investigator': {
                    'id': investigator.id,
                    'username': investigator.username,
                    'email': investigator.email
                }
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'المحقق المحدد غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def remove_investigator(self, request, pk=None):
        """إزالة محقق من التحقيق"""
        investigation = self.get_object()
        investigator_id = request.data.get('investigator_id')
        
        if not investigator_id:
            return Response(
                {'error': 'معرف المحقق مطلوب'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from accounts.models import User
            investigator = User.objects.get(id=investigator_id)
            investigation.assigned_investigators.remove(investigator)
            
            return Response({
                'message': f'تم إزالة {investigator.username} من المحققين بنجاح'
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'المحقق المحدد غير موجود'},
                status=status.HTTP_404_NOT_FOUND
            )


class AppealViewSet(viewsets.ModelViewSet):
    """ViewSet للاستئنافات"""
    
    queryset = Appeal.objects.all().select_related(
        'investigation', 'created_by', 'reviewed_by'
    )
    
    serializer_class = AppealSerializer
    permission_classes = [AppealPermissions]
    
    # فلاتر البحث والترتيب
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['investigation', 'status', 'created_by']
    search_fields = ['appeal_number', 'appellant_name', 'appeal_reason']
    ordering_fields = ['created_at', 'date_submitted', 'date_reviewed']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """تخصيص QuerySet حسب دور المستخدم"""
        user = self.request.user
        
        role_name = user.role_name
        if not role_name:
            return Appeal.objects.none()
        
        # President و GeneralManager: جميع الاستئنافات
        if role_name in ['President', 'GeneralManager']:
            return Appeal.objects.all()
        
        # DepartmentManager: استئنافات تحقيقات إدارته
        if role_name == 'DepartmentManager':
            return Appeal.objects.filter(investigation__department=user.department)
        
        # Lawyer: استئنافات التحقيقات المعينة له
        if role_name == 'Lawyer':
            return Appeal.objects.filter(
                Q(investigation__assigned_investigators=user) |
                Q(investigation__department=user.department)
            ).distinct()
        
        # Secretary: استئنافات التحقيقات المرتبطة بالمحامي المسؤول
        if role_name == 'Secretary':
            if user.assigned_lawyer:
                return Appeal.objects.filter(
                    investigation__assigned_investigators=user.assigned_lawyer
                ).distinct()
            return Appeal.objects.none()
        
        return Appeal.objects.none()
    
    def perform_create(self, serializer):
        """إنشاء استئناف جديد مع تعيين المنشئ"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """مراجعة الاستئناف وإصدار قرار"""
        appeal = self.get_object()
        
        # التحقق من الصلاحية للمراجعة
        user = request.user
        role_name = user.role_name
        if not role_name or role_name not in ['President', 'GeneralManager', 'DepartmentManager', 'Lawyer']:
            raise PermissionDenied("لا تملك صلاحية مراجعة الاستئنافات")
        
        decision = request.data.get('decision', '')
        new_status = request.data.get('status', 'under_review')
        notes = request.data.get('notes', '')
        
        # تحديث الاستئناف
        appeal.decision = decision
        appeal.status = new_status
        appeal.notes = notes
        appeal.reviewed_by = user
        appeal.date_reviewed = timezone.now().date()
        appeal.save()
        
        # تحديث حالة التحقيق إذا لزم الأمر
        if new_status == 'accepted':
            investigation = appeal.investigation
            investigation.status = 'appealed'
            investigation.save()
        
        serializer = self.get_serializer(appeal)
        return Response({
            'message': 'تم مراجعة الاستئناف بنجاح',
            'appeal': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def pending_reviews(self, request):
        """الاستئنافات المعلقة للمراجعة"""
        queryset = self.get_queryset().filter(status='submitted')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
