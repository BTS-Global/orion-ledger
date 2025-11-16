from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone

from .models import (
    AnnualReturn,
    EconomicSubstanceReport,
    JurisdictionFee,
    ExchangeRate,
    CorporateServiceClient
)
from .serializers import (
    AnnualReturnSerializer,
    AnnualReturnListSerializer,
    EconomicSubstanceReportSerializer,
    JurisdictionFeeSerializer,
    ExchangeRateSerializer,
    CurrencyConversionSerializer,
    CurrencyConversionResponseSerializer,
    CorporateServiceClientSerializer,
    CorporateServiceClientListSerializer,
)


class AnnualReturnViewSet(viewsets.ModelViewSet):
    """ViewSet for Annual Returns."""
    queryset = AnnualReturn.objects.select_related('company', 'created_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'filing_year', 'status']
    search_fields = ['company__name', 'reference_number']
    ordering_fields = ['filing_year', 'due_date', 'created_at']
    ordering = ['-filing_year', '-due_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AnnualReturnListSerializer
        return AnnualReturnSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue annual returns."""
        today = timezone.now().date()
        overdue_returns = self.queryset.filter(
            due_date__lt=today,
            status__in=['DRAFT', 'PENDING']
        )
        
        # Filter by company if provided
        company_id = request.query_params.get('company')
        if company_id:
            overdue_returns = overdue_returns.filter(company_id=company_id)
        
        serializer = self.get_serializer(overdue_returns, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming annual returns (due in next 60 days)."""
        today = timezone.now().date()
        upcoming_date = today + timezone.timedelta(days=60)
        
        upcoming_returns = self.queryset.filter(
            due_date__gte=today,
            due_date__lte=upcoming_date,
            status__in=['DRAFT', 'PENDING']
        )
        
        serializer = self.get_serializer(upcoming_returns, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF for this annual return."""
        annual_return = self.get_object()
        
        # TODO: Implement PDF generation logic
        # This would use ReportLab or WeasyPrint to generate the PDF
        
        return Response({
            'message': 'PDF generation is not yet implemented',
            'id': str(annual_return.id)
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class EconomicSubstanceReportViewSet(viewsets.ModelViewSet):
    """ViewSet for Economic Substance Reports."""
    queryset = EconomicSubstanceReport.objects.select_related('company', 'created_by').all()
    serializer_class = EconomicSubstanceReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'reporting_year', 'status', 'business_activity', 'meets_substance_requirements']
    search_fields = ['company__name', 'reference_number']
    ordering_fields = ['reporting_year', 'submission_deadline', 'created_at']
    ordering = ['-reporting_year']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assess(self, request, pk=None):
        """Auto-assess if substance requirements are met."""
        es_report = self.get_object()
        
        # Simple assessment logic
        # Can be made more sophisticated based on business rules
        assessment = {
            'has_adequate_employees': es_report.has_adequate_employees,
            'has_adequate_premises': es_report.has_adequate_premises,
            'has_adequate_expenditure': es_report.has_adequate_expenditure,
            'conducts_core_activities': es_report.conducts_core_activities,
        }
        
        # For holding companies, check reduced substance
        if es_report.business_activity == 'HOLDING':
            meets_requirements = es_report.is_pure_equity_holding and es_report.meets_reduced_substance
        else:
            meets_requirements = all(assessment.values())
        
        es_report.meets_substance_requirements = meets_requirements
        es_report.save()
        
        return Response({
            'meets_requirements': meets_requirements,
            'assessment': assessment,
            'message': 'Assessment completed'
        })
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF for this ES report."""
        es_report = self.get_object()
        
        # TODO: Implement PDF generation logic
        
        return Response({
            'message': 'PDF generation is not yet implemented',
            'id': str(es_report.id)
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class JurisdictionFeeViewSet(viewsets.ModelViewSet):
    """ViewSet for Jurisdiction Fees."""
    queryset = JurisdictionFee.objects.select_related('company').all()
    serializer_class = JurisdictionFeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'fee_type', 'status', 'currency']
    search_fields = ['company__name', 'description', 'payment_reference']
    ordering_fields = ['due_date', 'amount', 'created_at']
    ordering = ['-due_date']
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue fees."""
        today = timezone.now().date()
        overdue_fees = self.queryset.filter(
            due_date__lt=today,
            status__in=['PENDING', 'OVERDUE']
        )
        
        # Filter by company if provided
        company_id = request.query_params.get('company')
        if company_id:
            overdue_fees = overdue_fees.filter(company_id=company_id)
        
        serializer = self.get_serializer(overdue_fees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming fees (due in next 30 days)."""
        today = timezone.now().date()
        upcoming_date = today + timezone.timedelta(days=30)
        
        upcoming_fees = self.queryset.filter(
            due_date__gte=today,
            due_date__lte=upcoming_date,
            status='PENDING'
        )
        
        serializer = self.get_serializer(upcoming_fees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a fee as paid."""
        fee = self.get_object()
        
        paid_date = request.data.get('paid_date', timezone.now().date())
        payment_reference = request.data.get('payment_reference', '')
        
        fee.status = 'PAID'
        fee.paid_date = paid_date
        fee.payment_reference = payment_reference
        fee.save()
        
        serializer = self.get_serializer(fee)
        return Response(serializer.data)


class ExchangeRateViewSet(viewsets.ModelViewSet):
    """ViewSet for Exchange Rates."""
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['from_currency', 'to_currency', 'date', 'source']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    @action(detail=False, methods=['post'])
    def convert(self, request):
        """Convert amount from one currency to another."""
        serializer = CurrencyConversionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        from_currency = serializer.validated_data['from_currency']
        to_currency = serializer.validated_data['to_currency']
        date = serializer.validated_data['date']
        
        try:
            rate = ExchangeRate.get_rate(from_currency, to_currency, date)
            if rate is None:
                return Response({
                    'error': f'No exchange rate found for {from_currency} to {to_currency} on {date}'
                }, status=status.HTTP_404_NOT_FOUND)
            
            converted_amount = ExchangeRate.convert(amount, from_currency, to_currency, date)
            
            response_serializer = CurrencyConversionResponseSerializer(data={
                'amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': converted_amount,
                'rate': rate,
                'date': date
            })
            response_serializer.is_valid(raise_exception=True)
            
            return Response(response_serializer.data)
        
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest exchange rates for a currency pair."""
        from_currency = request.query_params.get('from_currency')
        to_currency = request.query_params.get('to_currency')
        
        if not from_currency or not to_currency:
            return Response({
                'error': 'from_currency and to_currency parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        latest_rate = ExchangeRate.objects.filter(
            from_currency=from_currency,
            to_currency=to_currency
        ).order_by('-date').first()
        
        if not latest_rate:
            return Response({
                'error': f'No exchange rate found for {from_currency} to {to_currency}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(latest_rate)
        return Response(serializer.data)


class CorporateServiceClientViewSet(viewsets.ModelViewSet):
    """ViewSet for Corporate Service Clients."""
    queryset = CorporateServiceClient.objects.select_related('relationship_manager').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['client_type', 'status', 'risk_rating', 'kyc_completed']
    search_fields = ['client_reference', 'client_name', 'email']
    ordering_fields = ['client_name', 'created_at', 'onboarding_date']
    ordering = ['client_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CorporateServiceClientListSerializer
        return CorporateServiceClientSerializer
    
    @action(detail=True, methods=['get'])
    def companies(self, request, pk=None):
        """Get all companies for this client."""
        client = self.get_object()
        companies = client.get_active_companies()
        
        from .serializers import CompanyOffshoreSerializer
        serializer = CompanyOffshoreSerializer(companies, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def kyc_review_due(self, request):
        """Get clients with KYC review due soon (next 30 days)."""
        today = timezone.now().date()
        review_due_date = today + timezone.timedelta(days=30)
        
        clients = self.queryset.filter(
            kyc_review_date__lte=review_due_date,
            kyc_review_date__gte=today,
            status='ACTIVE'
        )
        
        serializer = self.get_serializer(clients, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def kyc_overdue(self, request):
        """Get clients with overdue KYC review."""
        today = timezone.now().date()
        
        clients = self.queryset.filter(
            kyc_review_date__lt=today,
            status='ACTIVE'
        )
        
        serializer = self.get_serializer(clients, many=True)
        return Response(serializer.data)
