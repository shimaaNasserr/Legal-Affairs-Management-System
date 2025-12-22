"""
Management command لإدخال بيانات تجريبية مناسبة للنظام
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Role, Department
from cases.models import Case
from investigations.models import Investigation, Appeal
from contracts.models import Contract
from courts.models import Court, CourtDivision
from fatwas.models import Fatwa
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'إدخال بيانات تجريبية مناسبة للنظام'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed data...'))
        
        # 1. إنشاء الأدوار
        self.create_roles()
        
        # 2. إنشاء الإدارات
        departments = self.create_departments()
        
        # 3. إنشاء المستخدمين
        users = self.create_users(departments)
        
        # 4. إنشاء المحاكم
        courts = self.create_courts(departments)
        
        # 5. إنشاء القضايا
        self.create_cases(users, departments, courts)
        
        # 6. إنشاء التحقيقات
        investigations = self.create_investigations(users, departments)
        
        # 7. إنشاء الاستئنافات
        self.create_appeals(investigations, users, departments)
        
        # 8. إنشاء العقود
        self.create_contracts(users, departments)
        
        # 9. إنشاء الفتاوى (معلق مؤقتاً بسبب مشكلة migration)
        # self.create_fatwas(users, departments)
        
        # 10. ربط السكرتيرات بالمحامين
        self.link_secretaries_to_lawyers(users)
        
        self.stdout.write(self.style.SUCCESS('Data seeded successfully!'))

    def create_roles(self):
        """إنشاء الأدوار"""
        roles_data = [
            {'name': 'President', 'description': 'الرئيس - يملك جميع الصلاحيات'},
            {'name': 'GeneralManager', 'description': 'المدير العام - إدارة شاملة'},
            {'name': 'DepartmentManager', 'description': 'مدير الإدارة - إدارة إدارته فقط'},
            {'name': 'Lawyer', 'description': 'محامي - متابعة القضايا والتحقيقات'},
            {'name': 'Secretary', 'description': 'سكرتيرة - مساعدة المحامين'},
        ]
        
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(f'  Created role: {role.name}')
            else:
                self.stdout.write(f'  Role exists: {role.name}')

    def create_departments(self):
        """إنشاء الإدارات"""
        departments_data = [
            {'name': 'إدارة الشئون القانونية', 'code': 'LEGAL-001'},
            {'name': 'إدارة التحقيقات', 'code': 'INV-001'},
            {'name': 'إدارة العقود', 'code': 'CNT-001'},
            {'name': 'إدارة القضايا', 'code': 'CASE-001'},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'code': dept_data['code']}
            )
            departments.append(dept)
            if created:
                try:
                    self.stdout.write(f'  Created department: {dept.name}')
                except UnicodeEncodeError:
                    self.stdout.write(f'  Created department: {dept.code}')
        
        return departments

    def create_users(self, departments):
        """إنشاء المستخدمين"""
        users_data = [
            # President
            {'username': 'president1', 'email': 'president@psu.edu.eg', 'first_name': 'أحمد', 'last_name': 'محمد', 'role': 'President', 'department': 0},
            
            # General Manager
            {'username': 'gm1', 'email': 'gm@psu.edu.eg', 'first_name': 'فاطمة', 'last_name': 'علي', 'role': 'GeneralManager', 'department': 0},
            
            # Department Managers
            {'username': 'dept_mgr1', 'email': 'deptmgr1@psu.edu.eg', 'first_name': 'خالد', 'last_name': 'إبراهيم', 'role': 'DepartmentManager', 'department': 0},
            {'username': 'dept_mgr2', 'email': 'deptmgr2@psu.edu.eg', 'first_name': 'سارة', 'last_name': 'حسن', 'role': 'DepartmentManager', 'department': 1},
            
            # Lawyers
            {'username': 'lawyer1', 'email': 'lawyer1@psu.edu.eg', 'first_name': 'محمد', 'last_name': 'عبدالله', 'role': 'Lawyer', 'department': 0},
            {'username': 'lawyer2', 'email': 'lawyer2@psu.edu.eg', 'first_name': 'نورا', 'last_name': 'سعيد', 'role': 'Lawyer', 'department': 0},
            {'username': 'lawyer3', 'email': 'lawyer3@psu.edu.eg', 'first_name': 'يوسف', 'last_name': 'محمود', 'role': 'Lawyer', 'department': 1},
            
            # Secretaries
            {'username': 'secretary1', 'email': 'secretary1@psu.edu.eg', 'first_name': 'مريم', 'last_name': 'أحمد', 'role': 'Secretary', 'department': 0},
            {'username': 'secretary2', 'email': 'secretary2@psu.edu.eg', 'first_name': 'ليلى', 'last_name': 'عمر', 'role': 'Secretary', 'department': 0},
            {'username': 'secretary3', 'email': 'secretary3@psu.edu.eg', 'first_name': 'هند', 'last_name': 'خالد', 'role': 'Secretary', 'department': 1},
        ]
        
        users = {}
        for user_data in users_data:
            role = Role.objects.get(name=user_data['role'])
            department = departments[user_data['department']] if user_data['department'] < len(departments) else None
            
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'username': user_data['username'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': role,
                    'department': department,
                }
            )
            
            if created:
                user.set_password('password123')  # كلمة مرور افتراضية
                user.save()
                try:
                    self.stdout.write(f'  Created user: {user.username} ({user.role.name})')
                except UnicodeEncodeError:
                    self.stdout.write(f'  Created user: {user.username}')
            
            users[user_data['role']] = users.get(user_data['role'], []) + [user]
        
        return users

    def create_courts(self, departments):
        """إنشاء المحاكم"""
        courts_data = [
            {'name': 'محكمة بورسعيد الابتدائية', 'department': 0},
            {'name': 'محكمة الإسماعيلية الابتدائية', 'department': 0},
            {'name': 'محكمة الاستئناف - الدائرة الشرقية', 'department': 0},
            {'name': 'محكمة النقض', 'department': 0},
        ]
        
        courts = []
        for court_data in courts_data:
            court, created = Court.objects.get_or_create(
                name=court_data['name'],
                defaults={
                    'description': f'وصف {court_data["name"]}',
                    'department': departments[court_data['department']] if court_data['department'] < len(departments) else None
                }
            )
            courts.append(court)
            if created:
                # إنشاء أقسام للمحكمة
                divisions = ['القسم المدني', 'القسم التجاري', 'القسم الجنائي']
                for div_name in divisions:
                    CourtDivision.objects.get_or_create(
                        court=court,
                        name=div_name,
                        defaults={'note': f'ملاحظة عن {div_name}'}
                    )
                try:
                    self.stdout.write(f'  Created court: {court.name}')
                except UnicodeEncodeError:
                    self.stdout.write(f'  Created court with divisions')
        
        return courts

    def create_cases(self, users, departments, courts):
        """إنشاء القضايا"""
        lawyers = users.get('Lawyer', [])
        if not lawyers:
            self.stdout.write(self.style.WARNING('  No lawyers found to create cases'))
            return
        
        cases_data = [
            {
                'case_number': 'CASE-2024-001',
                'lawsuit_number': 'LAW-2024-001',
                'plaintiff': 'جامعة بورسعيد',
                'defendant': 'شركة البناء المحدودة',
                'requests': 'طلب التعويض عن الأضرار الناتجة عن عقد البناء',
                'case_status': 'in_court',
                'appeal_status': False,
                'department': 0,
            },
            {
                'case_number': 'CASE-2024-002',
                'lawsuit_number': 'LAW-2024-002',
                'plaintiff': 'أحمد محمد علي',
                'defendant': 'جامعة بورسعيد',
                'requests': 'طلب إلغاء قرار الفصل',
                'case_status': 'under_study',
                'appeal_status': None,
                'department': 0,
            },
            {
                'case_number': 'CASE-2024-003',
                'lawsuit_number': 'LAW-2024-003',
                'plaintiff': 'جامعة بورسعيد',
                'defendant': 'مؤسسة النظافة العامة',
                'requests': 'طلب تنفيذ عقد النظافة',
                'case_status': 'pending',
                'appeal_status': None,
                'department': 1,
            },
            {
                'case_number': 'CASE-2024-004',
                'lawsuit_number': 'LAW-2024-004',
                'plaintiff': 'فاطمة أحمد',
                'defendant': 'جامعة بورسعيد',
                'requests': 'طلب تعويض عن حادث',
                'case_status': 'closed',
                'appeal_status': True,
                'department': 0,
            },
        ]
        
        for i, case_data in enumerate(cases_data):
            case, created = Case.objects.get_or_create(
                case_number=case_data['case_number'],
                defaults={
                    'date_received': timezone.now().date() - timedelta(days=random.randint(10, 180)),
                    'lawsuit_number': case_data['lawsuit_number'],
                    'plaintiff': case_data['plaintiff'],
                    'defendant': case_data['defendant'],
                    'requests': case_data['requests'],
                    'case_status': case_data['case_status'],
                    'appeal_status': case_data['appeal_status'],
                    'department': departments[case_data['department']] if case_data['department'] < len(departments) else None,
                    'created_by': users.get('Lawyer', [users.get('DepartmentManager', [None])[0] if users.get('DepartmentManager') else None])[0] if users.get('Lawyer') else None,
                    'court': courts[i % len(courts)] if courts else None,
                    'hearing_dates': [(timezone.now().date() + timedelta(days=random.randint(7, 30))).isoformat()] if case_data['case_status'] == 'in_court' else [],
                    'notes': f'ملاحظات حول القضية {case_data["case_number"]}',
                }
            )
            
            if created:
                # ربط محاميين بالقضية
                if lawyers:
                    case.lawyers.set(random.sample(lawyers, min(2, len(lawyers))))
                self.stdout.write(f'  Created case: {case.case_number}')

    def create_investigations(self, users, departments):
        """إنشاء التحقيقات"""
        investigations_data = [
            {
                'title': 'تحقيق في مخالفة أكاديمية',
                'description': 'تحقيق في حالة غش في الامتحان',
                'accused_names': 'أحمد محمد, خالد إبراهيم',
                'status': 'under_investigation',
                'priority': 'high',
                'case_type': 'academic_misconduct',
                'complainant_type': 'faculty_member',
                'complainant_name': 'د. سارة حسن',
                'department': 1,
            },
            {
                'title': 'تحقيق في مخالفة إدارية',
                'description': 'تحقيق في تأخير في العمل',
                'accused_names': 'محمد عبدالله',
                'status': 'pending',
                'priority': 'medium',
                'case_type': 'administrative',
                'complainant_type': 'employee',
                'complainant_name': 'أحمد علي',
                'department': 0,
            },
            {
                'title': 'تحقيق في شكوى طالب',
                'description': 'شكوى من طالب حول معاملة غير لائقة',
                'accused_names': 'عضو هيئة تدريس',
                'status': 'completed',
                'priority': 'urgent',
                'case_type': 'internal_disciplinary',
                'complainant_type': 'student',
                'complainant_name': 'طالب مجهول',
                'department': 1,
            },
        ]
        
        investigations = []
        lawyers = users.get('Lawyer', [])
        
        for inv_data in investigations_data:
            investigation, created = Investigation.objects.get_or_create(
                title=inv_data['title'],
                defaults={
                    'description': inv_data['description'],
                    'accused_names': inv_data['accused_names'],
                    'date_received': timezone.now().date() - timedelta(days=random.randint(5, 90)),
                    'date_started': timezone.now().date() - timedelta(days=random.randint(1, 30)) if inv_data['status'] != 'pending' else None,
                    'date_completed': timezone.now().date() - timedelta(days=random.randint(1, 5)) if inv_data['status'] == 'completed' else None,
                    'status': inv_data['status'],
                    'priority': inv_data['priority'],
                    'case_type': inv_data['case_type'],
                    'complainant_type': inv_data['complainant_type'],
                    'complainant_name': inv_data['complainant_name'],
                    'department': departments[inv_data['department']] if inv_data['department'] < len(departments) else None,
                    'created_by': users.get('DepartmentManager', [users.get('Lawyer', [None])[0] if users.get('Lawyer') else None])[0] if users.get('DepartmentManager') else None,
                    'notes': f'ملاحظات حول التحقيق: {inv_data["title"]}',
                }
            )
            
            if created and lawyers:
                investigation.assigned_investigators.set([random.choice(lawyers)])
            
            investigations.append(investigation)
            if created:
                try:
                    self.stdout.write(f'  Created investigation: {investigation.title}')
                except UnicodeEncodeError:
                    self.stdout.write(f'  Created investigation: {investigation.general_number}')
        
        return investigations

    def create_appeals(self, investigations, users, departments):
        """إنشاء الاستئنافات"""
        if not investigations:
            return
        
        appeals_data = [
            {
                'appellant_name': 'أحمد محمد',
                'appeal_reason': 'عدم الرضا عن نتيجة التحقيق',
                'status': 'submitted',
                'investigation': 0,
            },
            {
                'appellant_name': 'خالد إبراهيم',
                'appeal_reason': 'طلب إعادة النظر في القرار',
                'status': 'under_review',
                'investigation': 0,
            },
        ]
        
        for appeal_data in appeals_data:
            if appeal_data['investigation'] < len(investigations):
                investigation = investigations[appeal_data['investigation']]
                appeal, created = Appeal.objects.get_or_create(
                    investigation=investigation,
                    appellant_name=appeal_data['appellant_name'],
                    defaults={
                        'appeal_reason': appeal_data['appeal_reason'],
                        'date_submitted': timezone.now().date() - timedelta(days=random.randint(1, 10)),
                        'status': appeal_data['status'],
                        'department': investigation.department,
                        'created_by': users.get('Lawyer', [users.get('DepartmentManager', [None])[0] if users.get('DepartmentManager') else None])[0] if users.get('Lawyer') else None,
                        'complainant': users.get('Lawyer', [None])[0] if users.get('Lawyer') else None,
                    }
                )
                if created:
                    self.stdout.write(f'  Created appeal: {appeal.appeal_number}')

    def create_contracts(self, users, departments):
        """إنشاء العقود"""
        contracts_data = [
            {
                'contract_number': 'CNT-2024-001',
                'contract_type': 'tender',
                'content': 'عقد توريد أجهزة حاسوب',
                'progress': 'تم التوقيع والتنفيذ',
                'department': 2,
            },
            {
                'contract_number': 'CNT-2024-002',
                'contract_type': 'direct',
                'content': 'عقد صيانة المباني',
                'progress': 'قيد التنفيذ',
                'department': 2,
            },
            {
                'contract_number': 'CNT-2024-003',
                'contract_type': 'practice',
                'content': 'عقد خدمات نظافة',
                'progress': 'تم التوقيع',
                'department': 2,
            },
        ]
        
        for contract_data in contracts_data:
            contract, created = Contract.objects.get_or_create(
                contract_number=contract_data['contract_number'],
                defaults={
                    'date_received': timezone.now().date() - timedelta(days=random.randint(30, 180)),
                    'contract_type': contract_data['contract_type'],
                    'content': contract_data['content'],
                    'progress': contract_data['progress'],
                    'department': departments[contract_data['department']] if contract_data['department'] < len(departments) else None,
                    'created_by': users.get('DepartmentManager', [users.get('Lawyer', [None])[0] if users.get('Lawyer') else None])[0] if users.get('DepartmentManager') else None,
                    'archive_date': timezone.now().date() - timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                }
            )
            if created:
                self.stdout.write(f'  Created contract: {contract.contract_number}')

    def create_fatwas(self, users, departments):
        """إنشاء الفتاوى"""
        fatwas_data = [
            {
                'request_content': 'طلب فتوى حول قانونية عقد معين',
                'result': 'العقد قانوني ومتوافق مع القوانين',
                'department': 0,
            },
            {
                'request_content': 'طلب فتوى حول إجراءات التعيين',
                'result': 'الإجراءات صحيحة ومتوافقة',
                'department': 0,
            },
        ]
        
        for fatwa_data in fatwas_data:
            # استخدام UUID كمعرف فريد بدلاً من request_content
            fatwa = Fatwa(
                request_content=fatwa_data['request_content'],
                result=fatwa_data['result'],
                department=departments[fatwa_data['department']] if fatwa_data['department'] < len(departments) else departments[0],
                created_by=users.get('Lawyer', [users.get('DepartmentManager', [None])[0] if users.get('DepartmentManager') else None])[0] if users.get('Lawyer') else None,
            )
            fatwa.save()
            created = True
            if created:
                self.stdout.write(f'  Created fatwa: {fatwa.general_number}')

    def link_secretaries_to_lawyers(self, users):
        """ربط السكرتيرات بالمحامين"""
        lawyers = users.get('Lawyer', [])
        secretaries = users.get('Secretary', [])
        
        if not lawyers or not secretaries:
            return
        
        # ربط كل سكرتيرة بمحامي
        # for i, secretary in enumerate(secretaries):
        #     lawyer = lawyers[i % len(lawyers)]
        #     secretary.assigned_lawyer = lawyer
        #     secretary.save()
            
        #     # إنشاء LawyerSecretaryAccess
        #     LawyerSecretaryAccess.objects.get_or_create(
        #         lawyer=lawyer,
        #         secretary=secretary
        #     )
        #     self.stdout.write(f'  Linked {secretary.username} to {lawyer.username}')

