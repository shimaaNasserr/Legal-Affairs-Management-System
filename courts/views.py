from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Court, CourtDivision
from .serializers import CourtSerializer, CourtDivisionSerializer
from .permissions import CourtPermission


class CourtListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CourtSerializer
    permission_classes = [IsAuthenticated, CourtPermission]

    def get_queryset(self):
        user = self.request.user
        role_name = user.role_name
        
        # President و GeneralManager: جميع المحاكم
        if role_name in ['President', 'GeneralManager']:
            return Court.objects.all()
        
        # DepartmentManager: محاكم إدارته فقط
        if role_name == 'DepartmentManager' and user.department:
            return Court.objects.filter(department=user.department)
        
        # باقي الأدوار: جميع المحاكم (للقراءة فقط)
        return Court.objects.all()


class CourtRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourtSerializer
    permission_classes = [IsAuthenticated, CourtPermission]
    queryset = Court.objects.all()


class CourtDivisionByCourtAPIView(generics.ListCreateAPIView):
    serializer_class = CourtDivisionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CourtDivision.objects.filter(court_id=self.kwargs["court_id"])

    def perform_create(self, serializer):
        court = Court.objects.get(id=self.kwargs["court_id"])
        serializer.save(court=court)
