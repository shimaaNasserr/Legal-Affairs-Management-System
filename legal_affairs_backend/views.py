from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from cases.models import Case
from contracts.models import Contract
from fatwas.models import Fatwa
from investigations.models import Investigation


class ReportsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Basic totals; can be extended to filter by role/department later
        data = {
            "cases": Case.objects.count(),
            "contracts": Contract.objects.count(),
            "fatwas": Fatwa.objects.count(),
            "investigations": Investigation.objects.count(),
        }
        return Response(data)


class CasesByStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Aggregate cases by status
        qs = Case.objects.values('status').annotate(count=Count('id')).order_by('status')
        data = {row['status'] or 'unknown': row['count'] for row in qs}
        return Response(data)


class ContractsByTypeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Aggregate contracts by type
        qs = Contract.objects.values('contract_type').annotate(count=Count('id')).order_by('contract_type')
        data = {row['contract_type'] or 'unknown': row['count'] for row in qs}
        return Response(data)
