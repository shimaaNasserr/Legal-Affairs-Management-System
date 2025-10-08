import os
import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import User, Role, Department
from .models import Investigation, Appeal


class InvestigationModelTest(TestCase):
    """اختبارات نموذج Investigation"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        # إنشاء الأدوار
        self.president_role = Role.objects.create(name='President')
        self.lawyer_role = Role.objects.create(name='Lawyer')
        
        # إنشاء الإدارة
        self.department = Department.objects.create(
            name='الإدارة القانونية',
            code='LEGAL'
        )
        
        # إنشاء المستخدمين
        self.president = User.objects.create_user(
            username='president',
            email='president@test.com',
            password='testpass123',
            role=self.president_role,
            department=self.department
        )
        
        self.lawyer = User.objects.create_user(
            username='lawyer',
            email='lawyer@test.com',
            password='testpass123',
            role=self.lawyer_role,
            department=self.department
        )
    
    def test_investigation_creation(self):
        """اختبار إنشاء تحقيق جديد"""
        investigation = Investigation.objects.create(
            title='تحقيق اختبار',
            description='وصف التحقيق',
            accused_names='أحمد محمد, سارة علي',
            date_received=timezone.now().date(),
            department=self.department,
            created_by=self.lawyer
        )
        
        self.assertEqual(investigation.title, 'تحقيق اختبار')
        self.assertTrue(investigation.general_number.startswith('INV-'))
        self.assertEqual(investigation.status, 'pending')
        self.assertEqual(investigation.priority, 'medium')
    
    def test_general_number_auto_generation(self):
        """اختبار التوليد التلقائي للرقم العام"""
        investigation = Investigation.objects.create(
            title='تحقيق اختبار',
            description='وصف التحقيق',
            accused_names='أحمد محمد',
            date_received=timezone.now().date(),
            department=self.department,
            created_by=self.lawyer
        )
        
        self.assertIsNotNone(investigation.general_number)
        self.assertTrue(investigation.general_number.startswith('INV-'))
        
        # اختبار عدم التكرار
        investigation2 = Investigation.objects.create(
            title='تحقيق اختبار 2',
            description='وصف التحقيق 2',
            accused_names='علي أحمد',
            date_received=timezone.now().date(),
            department=self.department,
            created_by=self.lawyer
        )
        
        self.assertNotEqual(investigation.general_number, investigation2.general_number)
    
    def test_accused_names_methods(self):
        """اختبار دوال أسماء المتهمين"""
        investigation = Investigation.objects.create(
            title='تحقيق اختبار',
            description='وصف التحقيق',
            accused_names='أحمد محمد, سارة علي, محمد حسن',
            date_received=timezone.now().date(),
            department=self.department,
            created_by=self.lawyer
        )
        
        names_list = investigation.get_accused_names_list()
        self.assertEqual(len(names_list), 3)
        self.assertIn('أحمد محمد', names_list)
        self.assertIn('سارة علي', names_list)
        
        # اختبار تعيين قائمة جديدة
        new_names = ['علي أحمد', 'فاطمة محمد']
        investigation.set_accused_names_list(new_names)
        self.assertEqual(investigation.accused_names, 'علي أحمد, فاطمة محمد')


class AppealModelTest(TestCase):
    """اختبارات نموذج Appeal"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.lawyer_role = Role.objects.create(name='Lawyer')
        self.department = Department.objects.create(name='الإدارة القانونية', code='LEGAL')
        
        self.lawyer = User.objects.create_user(
            username='lawyer',
            email='lawyer@test.com',
            password='testpass123',
            role=self.lawyer_role,
            department=self.department
        )
        
        self.investigation = Investigation.objects.create(
            title='تحقيق اختبار',
            description='وصف التحقيق',
            accused_names='أحمد محمد',
            date_received=timezone.now().date(),
            department=self.department,
            created_by=self.lawyer
        )
    
    def test_appeal_creation(self):
        """اختبار إنشاء استئناف جديد"""
        appeal = Appeal.objects.create(
            investigation=self.investigation,
            appeal_number='APP-2024-001',
            appellant_name='أحمد محمد',
            appeal_reason='عدم عدالة الإجراءات',
            date_submitted=timezone.now().date(),
            created_by=self.lawyer
        )
        
        self.assertEqual(appeal.appellant_name, 'أحمد محمد')
        self.assertEqual(appeal.status, 'submitted')
        self.assertEqual(appeal.investigation, self.investigation)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class InvestigationAPITest(APITestCase):
    """اختبارات API للتحقيقات"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        # إنشاء الأدوار
        self.president_role = Role.objects.create(name='President')
        self.manager_role = Role.objects.create(name='DepartmentManager')
        self.lawyer_role = Role.objects.create(name='Lawyer')
        self.secretary_role = Role.objects.create(name='Secretary')
        
        # إنشاء الإدارات
        self.department1 = Department.objects.create(name='الإدارة القانونية', code='LEGAL')
        self.department2 = Department.objects.create(name='إدارة أخرى', code='OTHER')
        
        # إنشاء المستخدمين
        self.president = User.objects.create_user(
            username='president',
            email='president@test.com',
            password='testpass123',
            role=self.president_role,
            department=self.department1
        )
        
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass123',
            role=self.manager_role,
            department=self.department1
        )
        
        self.lawyer = User.objects.create_user(
            username='lawyer',
            email='lawyer@test.com',
            password='testpass123',
            role=self.lawyer_role,
            department=self.department1
        )
        
        self.secretary = User.objects.create_user(
            username='secretary',
            email='secretary@test.com',
            password='testpass123',
            role=self.secretary_role,
            department=self.department1,
            assigned_lawyer=self.lawyer
        )
        
        self.other_lawyer = User.objects.create_user(
            username='other_lawyer',
            email='other_lawyer@test.com',
            password='testpass123',
            role=self.lawyer_role,
            department=self.department2
        )
        
        # إنشاء تحقيق للاختبار
        self.investigation = Investigation.objects.create(
            title='تحقيق اختبار',
            description='وصف التحقيق',
            accused_names='أحمد محمد',
            date_received=timezone.now().date(),
            department=self.department1,
            created_by=self.lawyer
        )
        self.investigation.assigned_investigators.add(self.lawyer)
        
        self.client = APIClient()
    
    def test_president_full_access(self):
        """اختبار صلاحيات الرئيس الكاملة"""
        self.client.force_authenticate(user=self.president)
        
        # اختبار العرض
        response = self.client.get('/api/investigations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # اختبار الإنشاء
        data = {
            'title': 'تحقيق جديد',
            'description': 'وصف التحقيق الجديد',
            'accused_names': 'سارة علي',
            'date_received': timezone.now().date(),
            'department': self.department1.id
        }
        response = self.client.post('/api/investigations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # اختبار التحديث
        response = self.client.patch(f'/api/investigations/{self.investigation.id}/', {
            'title': 'تحقيق محدث'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # اختبار الحذف
        response = self.client.delete(f'/api/investigations/{self.investigation.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_department_manager_access(self):
        """اختبار صلاحيات مدير الإدارة"""
        self.client.force_authenticate(user=self.manager)
        
        # يمكنه عرض تحقيقات إدارته
        response = self.client.get('/api/investigations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # يمكنه إنشاء تحقيق في إدارته
        data = {
            'title': 'تحقيق مدير الإدارة',
            'description': 'وصف التحقيق',
            'accused_names': 'محمد أحمد',
            'date_received': timezone.now().date(),
            'department': self.department1.id
        }
        response = self.client.post('/api/investigations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_lawyer_access(self):
        """اختبار صلاحيات المحامي"""
        self.client.force_authenticate(user=self.lawyer)
        
        # يمكنه عرض التحقيقات المعينة له
        response = self.client.get('/api/investigations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # يمكنه تحديث التحقيقات المعينة له
        response = self.client.patch(f'/api/investigations/{self.investigation.id}/', {
            'notes': 'ملاحظات جديدة'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_secretary_access(self):
        """اختبار صلاحيات السكرتيرة"""
        self.client.force_authenticate(user=self.secretary)
        
        # يمكنها عرض التحقيقات المرتبطة بالمحامي المسؤول
        response = self.client.get('/api/investigations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthorized_access(self):
        """اختبار منع الوصول غير المصرح"""
        self.client.force_authenticate(user=self.other_lawyer)
        
        # لا يمكنه تحديث تحقيق ليس معيناً له
        response = self.client.patch(f'/api/investigations/{self.investigation.id}/', {
            'title': 'محاولة تحديث غير مصرح'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_file_upload(self):
        """اختبار رفع الملفات"""
        self.client.force_authenticate(user=self.lawyer)
        
        # إنشاء ملف اختبار
        test_file = SimpleUploadedFile(
            "test_document.txt",
            b"محتوى الملف الاختباري",
            content_type="text/plain"
        )
        
        data = {
            'title': 'تحقيق مع ملف',
            'description': 'وصف التحقيق',
            'accused_names': 'أحمد محمد',
            'date_received': timezone.now().date(),
            'department': self.department1.id,
            'file': test_file
        }
        
        response = self.client.post('/api/investigations/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file', response.data)
    
    def test_investigation_stats(self):
        """اختبار إحصائيات التحقيقات"""
        self.client.force_authenticate(user=self.president)
        
        response = self.client.get('/api/investigations/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # التحقق من وجود الحقول المطلوبة
        required_fields = [
            'total', 'pending', 'under_investigation', 'completed',
            'closed', 'appealed', 'low_priority', 'medium_priority',
            'high_priority', 'urgent_priority', 'this_month', 'last_month'
        ]
        
        for field in required_fields:
            self.assertIn(field, response.data)
    
    def test_assign_investigator(self):
        """اختبار تعيين محقق"""
        self.client.force_authenticate(user=self.president)
        
        response = self.client.post(
            f'/api/investigations/{self.investigation.id}/assign_investigator/',
            {'investigator_id': self.manager.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # التحقق من إضافة المحقق
        self.investigation.refresh_from_db()
        self.assertIn(self.manager, self.investigation.assigned_investigators.all())


class AppealAPITest(APITestCase):
    """اختبارات API للاستئنافات"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        self.lawyer_role = Role.objects.create(name='Lawyer')
        self.president_role = Role.objects.create(name='President')
        
        self.department = Department.objects.create(name='الإدارة القانونية', code='LEGAL')
        
        self.lawyer = User.objects.create_user(
            username='lawyer',
            email='lawyer@test.com',
            password='testpass123',
            role=self.lawyer_role,
            department=self.department
        )
        
        self.president = User.objects.create_user(
            username='president',
            email='president@test.com',
            password='testpass123',
            role=self.president_role,
            department=self.department
        )
        
        self.investigation = Investigation.objects.create(
            title='تحقيق اختبار',
            description='وصف التحقيق',
            accused_names='أحمد محمد',
            date_received=timezone.now().date(),
            department=self.department,
            created_by=self.lawyer
        )
        
        self.appeal = Appeal.objects.create(
            investigation=self.investigation,
            appeal_number='APP-2024-001',
            appellant_name='أحمد محمد',
            appeal_reason='عدم عدالة الإجراءات',
            date_submitted=timezone.now().date(),
            created_by=self.lawyer
        )
        
        self.client = APIClient()
    
    def test_appeal_creation(self):
        """اختبار إنشاء استئناف جديد"""
        self.client.force_authenticate(user=self.lawyer)
        
        data = {
            'investigation': self.investigation.id,
            'appeal_number': 'APP-2024-002',
            'appellant_name': 'سارة علي',
            'appeal_reason': 'عدم كفاية الأدلة',
            'date_submitted': timezone.now().date()
        }
        
        response = self.client.post('/api/appeals/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_appeal_review(self):
        """اختبار مراجعة الاستئناف"""
        self.client.force_authenticate(user=self.president)
        
        data = {
            'decision': 'تم قبول الاستئناف',
            'status': 'accepted',
            'notes': 'ملاحظات المراجعة'
        }
        
        response = self.client.post(f'/api/appeals/{self.appeal.id}/review/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # التحقق من تحديث الاستئناف
        self.appeal.refresh_from_db()
        self.assertEqual(self.appeal.status, 'accepted')
        self.assertEqual(self.appeal.decision, 'تم قبول الاستئناف')
        self.assertEqual(self.appeal.reviewed_by, self.president)
    
    def test_pending_reviews(self):
        """اختبار عرض الاستئنافات المعلقة"""
        self.client.force_authenticate(user=self.president)
        
        response = self.client.get('/api/appeals/pending_reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # التحقق من وجود الاستئناف المعلق
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.appeal.id))


class InvestigationValidationTest(TestCase):
    """اختبارات التحقق من صحة البيانات"""
    
    def setUp(self):
        self.lawyer_role = Role.objects.create(name='Lawyer')
        self.department = Department.objects.create(name='الإدارة القانونية', code='LEGAL')
        
        self.lawyer = User.objects.create_user(
            username='lawyer',
            email='lawyer@test.com',
            password='testpass123',
            role=self.lawyer_role,
            department=self.department
        )
    
    def test_future_date_validation(self):
        """اختبار منع التواريخ المستقبلية"""
        from django.core.exceptions import ValidationError
        
        future_date = timezone.now().date() + timezone.timedelta(days=1)
        
        investigation = Investigation(
            title='تحقيق اختبار',
            description='وصف التحقيق',
            accused_names='أحمد محمد',
            date_received=future_date,
            department=self.department,
            created_by=self.lawyer
        )
        
        with self.assertRaises(ValidationError):
            investigation.full_clean()
    
    def test_date_sequence_validation(self):
        """اختبار تسلسل التواريخ"""
        from django.core.exceptions import ValidationError
        
        base_date = timezone.now().date()
        
        investigation = Investigation(
            title='تحقيق اختبار',
            description='وصف التحقيق',
            accused_names='أحمد محمد',
            date_received=base_date,
            date_started=base_date - timezone.timedelta(days=1),  # تاريخ بداية قبل الاستلام
            department=self.department,
            created_by=self.lawyer
        )
        
        with self.assertRaises(ValidationError):
            investigation.full_clean()
