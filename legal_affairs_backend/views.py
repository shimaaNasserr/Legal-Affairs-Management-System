from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cases.models import Case
from contracts.models import Contract
from fatwas.models import Fatwa
from investigations.models import Investigation
from investigations.models import Appeal


class ReportsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Basic totals; can be extended to filter by role/department later
        data = {
            "cases": Case.objects.count(),
            "contracts": Contract.objects.count(),
            "fatwas": Fatwa.objects.count(),
            "investigations": Investigation.objects.count(),
            "appeals": Appeal.objects.count(),
        }
        return Response(data)
