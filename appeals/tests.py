from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from investigations.models import Appeal
from accounts.models import Department
from investigations.models import Investigation

User = get_user_model()

class AppealModelTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Test Department")
        self.user = User.objects.create_user(
            username="testuser", 
            email="test@example.com", 
            password="testpass123",
            department=self.department
        )
        self.investigation = Investigation.objects.create(
            title="Test Investigation",
            description="Test description",
            accused_names="Test Accused",
            department=self.department,
            created_by=self.user
        )
    
    def test_appeal_creation(self):
        appeal = Appeal.objects.create(
            investigation=self.investigation,
            complainant=self.user,
            appellant_name="Test Appellant",
            appeal_reason="Test reason",
            date_submitted="2024-01-01",
            created_by=self.user
        )
        self.assertEqual(appeal.investigation, self.investigation)
        self.assertEqual(appeal.complainant, self.user)
        self.assertTrue(appeal.appeal_number)

class AppealAPITest(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Test Department")
        self.president = User.objects.create_user(
            username="president",
            email="president@example.com",
            password="testpass123",
            role="president"
        )
        self.department_manager = User.objects.create_user(
            username="deptmanager",
            email="manager@example.com",
            password="testpass123",
            role="department_manager",
            department=self.department
        )
        self.lawyer = User.objects.create_user(
            username="lawyer",
            email="lawyer@example.com",
            password="testpass123",
            role="lawyer"
        )
        self.investigation = Investigation.objects.create(
            title="Test Investigation",
            description="Test description",
            accused_names="Test Accused",
            department=self.department,
            created_by=self.president
        )
        self.appeal_data = {
            "investigation": str(self.investigation.id),
            "complainant": str(self.lawyer.id),
            "appellant_name": "Test Appellant",
            "appeal_reason": "Test appeal reason",
            "date_submitted": "2024-01-01"
        }
    
    def test_president_can_create_appeal(self):
        self.client.force_authenticate(user=self.president)
        response = self.client.post('/api/appeals/', self.appeal_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_department_manager_permissions(self):
        self.client.force_authenticate(user=self.department_manager)
        response = self.client.get('/api/appeals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)