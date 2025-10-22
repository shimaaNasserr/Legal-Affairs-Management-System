from django.core.management.base import BaseCommand
from accounts.models import Role

class Command(BaseCommand):
    help = "Create default roles"

    def handle(self, *args, **kwargs):
        roles = [
            ("president", "رئيس الجامعة"),
            ("general_manager", "مدير عام الإدارة"),
            ("department_manager", "مدير الإدارة المختص"),
            ("lawyer", "محامي"),
            ("secretary", "سكرتارية"),
        ]
        for name, desc in roles:
            Role.objects.get_or_create(name=name, defaults={"description": desc})
        self.stdout.write(self.style.SUCCESS(" Default roles created successfully!"))
