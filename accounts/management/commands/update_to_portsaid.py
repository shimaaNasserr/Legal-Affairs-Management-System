"""
Management command لتحديث البيانات الموجودة لتكون خاصة بجامعة بورسعيد
"""
from django.core.management.base import BaseCommand
from accounts.models import User
from cases.models import Case
from courts.models import Court
from django.db.models import Q


class Command(BaseCommand):
    help = 'تحديث البيانات الموجودة لتكون خاصة بجامعة بورسعيد'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to update data to Port Said University...'))
        
        # 1. تحديث البريد الإلكتروني للمستخدمين
        self.update_user_emails()
        
        # 2. تحديث القضايا
        self.update_cases()
        
        # 3. تحديث المحاكم
        self.update_courts()
        
        self.stdout.write(self.style.SUCCESS('Data updated successfully!'))

    def update_user_emails(self):
        """تحديث البريد الإلكتروني للمستخدمين"""
        users_updated = 0
        for user in User.objects.filter(email__contains='@university.edu'):
            old_email = user.email
            new_email = user.email.replace('@university.edu', '@psu.edu.eg')
            user.email = new_email
            user.save()
            users_updated += 1
            try:
                self.stdout.write(f'  Updated user email: {old_email} -> {new_email}')
            except UnicodeEncodeError:
                self.stdout.write(f'  Updated user email: {user.username}')
        
        if users_updated > 0:
            self.stdout.write(self.style.SUCCESS(f'  Updated {users_updated} user emails'))
        else:
            self.stdout.write('  No user emails to update')

    def update_cases(self):
        """تحديث القضايا"""
        cases_updated = 0
        
        # تحديث المدعي
        cases = Case.objects.filter(plaintiff__icontains='جامعة القاهرة')
        for case in cases:
            case.plaintiff = case.plaintiff.replace('جامعة القاهرة', 'جامعة بورسعيد')
            case.save()
            cases_updated += 1
        
        # تحديث المدعى عليه
        cases = Case.objects.filter(defendant__icontains='جامعة القاهرة')
        for case in cases:
            case.defendant = case.defendant.replace('جامعة القاهرة', 'جامعة بورسعيد')
            case.save()
            cases_updated += 1
        
        if cases_updated > 0:
            self.stdout.write(self.style.SUCCESS(f'  Updated {cases_updated} cases'))
        else:
            self.stdout.write('  No cases to update')

    def update_courts(self):
        """تحديث المحاكم"""
        courts_updated = 0
        
        # تحديث محكمة القاهرة
        courts = Court.objects.filter(name__icontains='القاهرة')
        for court in courts:
            court.name = court.name.replace('القاهرة', 'بورسعيد')
            court.description = court.description.replace('القاهرة', 'بورسعيد') if court.description else None
            court.save()
            courts_updated += 1
        
        # تحديث محكمة الجيزة
        courts = Court.objects.filter(name__icontains='الجيزة')
        for court in courts:
            court.name = court.name.replace('الجيزة', 'الإسماعيلية')
            court.description = court.description.replace('الجيزة', 'الإسماعيلية') if court.description else None
            court.save()
            courts_updated += 1
        
        if courts_updated > 0:
            self.stdout.write(self.style.SUCCESS(f'  Updated {courts_updated} courts'))
        else:
            self.stdout.write('  No courts to update')


