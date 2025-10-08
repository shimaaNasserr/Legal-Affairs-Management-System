from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestigationViewSet, AppealViewSet

# إنشاء Router للـ ViewSets
router = DefaultRouter()
router.register(r'investigations', InvestigationViewSet, basename='investigation')
router.register(r'appeals', AppealViewSet, basename='appeal')

urlpatterns = [
    # تضمين جميع URLs من Router
    path('', include(router.urls)),
]

# URLs المتاحة:
# GET /api/investigations/ - قائمة التحقيقات
# POST /api/investigations/ - إنشاء تحقيق جديد
# GET /api/investigations/{id}/ - تفاصيل تحقيق محدد
# PUT /api/investigations/{id}/ - تحديث تحقيق كامل
# PATCH /api/investigations/{id}/ - تحديث جزئي لتحقيق
# DELETE /api/investigations/{id}/ - حذف تحقيق

# GET /api/investigations/my-investigations/ - التحقيقات الخاصة بالمستخدم
# GET /api/investigations/stats/ - إحصائيات التحقيقات
# POST /api/investigations/{id}/assign_investigator/ - تعيين محقق
# DELETE /api/investigations/{id}/remove_investigator/ - إزالة محقق

# GET /api/appeals/ - قائمة الاستئنافات
# POST /api/appeals/ - إنشاء استئناف جديد
# GET /api/appeals/{id}/ - تفاصيل استئناف محدد
# PUT /api/appeals/{id}/ - تحديث استئناف كامل
# PATCH /api/appeals/{id}/ - تحديث جزئي لاستئناف
# DELETE /api/appeals/{id}/ - حذف استئناف

# POST /api/appeals/{id}/review/ - مراجعة الاستئناف
# GET /api/appeals/pending_reviews/ - الاستئنافات المعلقة للمراجعة
