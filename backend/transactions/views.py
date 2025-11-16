from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Transaction, JournalEntry, JournalEntryLine
from .serializers import (
    TransactionSerializer, 
    TransactionValidateSerializer,
    JournalEntrySerializer
)
from companies.models import Company, ChartOfAccounts
from .account_mapper import AccountMapper


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction CRUD operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        """Return transactions for companies accessible to the current user."""
        if self.request.user.is_authenticated:
            user = self.request.user
            accessible_companies = Company.objects.filter(owner=user) | Company.objects.filter(users=user)
            queryset = Transaction.objects.filter(company__in=accessible_companies)
        else:
            queryset = Transaction.objects.all()
        
        # Filter by company if provided
        company_id = self.request.query_params.get('company', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filter by validation status
        is_validated = self.request.query_params.get('validated', None)
        if is_validated is not None:
            queryset = queryset.filter(is_validated=is_validated.lower() == 'true')
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending (unvalidated) transactions."""
        queryset = self.get_queryset().filter(is_validated=False)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Mark transaction as validated and create journal entry."""
        transaction = self.get_object()
        transaction.is_validated = True
        transaction.validated_at = timezone.now()
        if request.user.is_authenticated:
            transaction.validated_by = request.user
        transaction.save()
        
        # Create journal entry if transaction has an account assigned
        if transaction.account:
            from .accounting_service import AccountingService
            try:
                AccountingService.create_journal_entry_from_transaction(transaction)
            except Exception as e:
                # Log error but don't fail validation
                print(f"Error creating journal entry: {e}")
        
        return Response(
            TransactionSerializer(transaction).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def validate_transaction(self, request, pk=None):
        """Validate a transaction and assign it to an account."""
        transaction = self.get_object()
        
        if transaction.is_validated:
            return Response(
                {'error': 'Transaction is already validated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TransactionValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        account_id = serializer.validated_data['account']
        
        try:
            account = ChartOfAccounts.objects.get(id=account_id, company=transaction.company)
        except ChartOfAccounts.DoesNotExist:
            return Response(
                {'error': 'Account not found or does not belong to this company'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update transaction
        transaction.account = account
        transaction.is_validated = True
        transaction.validated_by = request.user
        transaction.validated_at = timezone.now()
        transaction.save()
        
        return Response(
            TransactionSerializer(transaction).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def suggest_account(self, request):
        """Suggest accounts for a transaction based on description and amount."""
        description = request.data.get('description', '')
        amount = request.data.get('amount', None)
        company_id = request.data.get('company', None)
        
        if not description:
            return Response(
                {'error': 'Description is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not company_id:
            return Response(
                {'error': 'Company ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Use AccountMapper to get suggestions
        mapper = AccountMapper(company)
        suggestions = mapper.suggest_account(description, amount)
        
        return Response({
            'suggestions': suggestions,
            'count': len(suggestions)
        })
    
    @action(detail=False, methods=['get'])
    def account_statistics(self, request):
        """Get account usage statistics for a company."""
        company_id = request.query_params.get('company', None)
        
        if not company_id:
            return Response(
                {'error': 'Company ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        mapper = AccountMapper(company)
        stats = mapper.get_account_statistics()
        
        return Response(stats)


class JournalEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for Journal Entry CRUD operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    serializer_class = JournalEntrySerializer
    
    def get_queryset(self):
        """Return journal entries for companies accessible to the current user."""
        if self.request.user.is_authenticated:
            user = self.request.user
            accessible_companies = Company.objects.filter(owner=user) | Company.objects.filter(users=user)
            queryset = JournalEntry.objects.filter(company__in=accessible_companies)
        else:
            queryset = JournalEntry.objects.all()
        
        # Filter by company if provided
        company_id = self.request.query_params.get('company', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset

