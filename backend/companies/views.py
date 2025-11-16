from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from decimal import Decimal

from .models import Company, UserProfile, ChartOfAccounts
from .serializers import (
    CompanySerializer, 
    CompanyDetailSerializer,
    UserProfileSerializer, 
    ChartOfAccountsSerializer
)
from .coa_generator import DefaultCOAGenerator
from transactions.models import JournalEntryLine


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for Company CRUD operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    
    def get_queryset(self):
        """Return companies owned by or accessible to the current user."""
        # NOTE: Authentication temporarily disabled for development
        # Will be re-enabled in authentication phase
        # if self.request.user.is_authenticated:
        #     user = self.request.user
        #     return Company.objects.filter(owner=user) | Company.objects.filter(users=user)
        return Company.objects.all()
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return CompanySerializer
    
    def perform_create(self, serializer):
        """Set the owner to the current user when creating a company."""
        company = serializer.save(owner=self.request.user)
        # Add owner to users as well
        company.users.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Set this company as the active company for the current user."""
        company = self.get_object()
        
        # NOTE: Authentication temporarily disabled for development
        # Will be re-enabled in authentication phase
        if not request.user.is_authenticated:
            return Response({
                'status': 'success',
                'message': f'{company.name} is now your active company (auth disabled)'
            })
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'full_name': request.user.get_full_name() or request.user.username}
        )
        
        profile.active_company = company
        profile.save()
        
        return Response({
            'status': 'success',
            'message': f'{company.name} is now your active company'
        })
    
    @action(detail=True, methods=['post'])
    def initialize_default_coa(self, request, pk=None):
        """Initialize default Chart of Accounts for this company."""
        company = self.get_object()
        overwrite = request.data.get('overwrite', False)
        
        result = DefaultCOAGenerator.generate(company, overwrite=overwrite)
        
        if result['status'] == 'success':
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def default_coa_preview(self, request, pk=None):
        """Get preview of default accounts that would be created."""
        accounts = DefaultCOAGenerator.get_default_accounts_preview()
        
        return Response({
            'total_accounts': len(accounts),
            'accounts': accounts
        })
    
    @action(detail=True, methods=['get'])
    def coa_coverage_analysis(self, request, pk=None):
        """Analyze Chart of Accounts coverage and suggest improvements."""
        company = self.get_object()
        
        # Get existing accounts
        accounts = ChartOfAccounts.objects.filter(company=company)
        total_accounts = accounts.count()
        
        # Count by type
        by_type = {}
        for account in accounts:
            acc_type = account.account_type
            by_type[acc_type] = by_type.get(acc_type, 0) + 1
        
        # Get default accounts that are missing
        default_codes = {acc['code'] for acc in DefaultCOAGenerator.DEFAULT_ACCOUNTS}
        existing_codes = set(accounts.values_list('account_code', flat=True))
        missing_codes = default_codes - existing_codes
        
        missing_accounts = [
            acc for acc in DefaultCOAGenerator.DEFAULT_ACCOUNTS
            if acc['code'] in missing_codes
        ]
        
        # Check for duplicate names
        account_names = list(accounts.values_list('account_name', flat=True))
        duplicates = [name for name in set(account_names) if account_names.count(name) > 1]
        
        return Response({
            'total_accounts': total_accounts,
            'by_type': by_type,
            'missing_recommended_count': len(missing_accounts),
            'missing_recommended': missing_accounts[:10],  # First 10
            'duplicate_names': duplicates,
            'has_basic_structure': total_accounts >= 20,
            'coverage_percentage': min(100, int((total_accounts / len(default_codes)) * 100))
        })


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):
        """Return only the current user's profile."""
        if self.request.user.is_authenticated:
            return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.none()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get the current user's profile."""
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'full_name': request.user.get_full_name() or request.user.username}
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class ChartOfAccountsViewSet(viewsets.ModelViewSet):
    """ViewSet for Chart of Accounts CRUD operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    serializer_class = ChartOfAccountsSerializer
    
    def get_queryset(self):
        """Return accounts for companies accessible to the current user."""
        if self.request.user.is_authenticated:
            user = self.request.user
            accessible_companies = Company.objects.filter(owner=user) | Company.objects.filter(users=user)
            queryset = ChartOfAccounts.objects.filter(company__in=accessible_companies)
        else:
            queryset = ChartOfAccounts.objects.all()
        
        # Filter by company if provided
        company_id = self.request.query_params.get('company', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filter by account type if provided
        account_type = self.request.query_params.get('type', None)
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Calculate current balance for this account."""
        account = self.get_object()
        
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Build query
        query = Q(account=account)
        if start_date:
            query &= Q(journal_entry__date__gte=start_date)
        if end_date:
            query &= Q(journal_entry__date__lte=end_date)
        
        # Get journal entry lines for this account
        lines = JournalEntryLine.objects.filter(query)
        
        # Calculate balance
        debits = lines.aggregate(total=Sum('debit'))['total'] or Decimal('0')
        credits = lines.aggregate(total=Sum('credit'))['total'] or Decimal('0')
        
        # Normal balance depends on account type
        if account.account_type in ['ASSET', 'EXPENSE']:
            balance = debits - credits
        else:  # LIABILITY, EQUITY, REVENUE
            balance = credits - debits
        
        return Response({
            'account_id': str(account.id),
            'account_code': account.account_code,
            'account_name': account.account_name,
            'account_type': account.account_type,
            'balance': float(balance),
            'debits': float(debits),
            'credits': float(credits),
            'start_date': start_date,
            'end_date': end_date
        })
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get accounts in hierarchical tree structure."""
        company_id = request.query_params.get('company')
        if not company_id:
            return Response(
                {'error': 'company parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        accounts = ChartOfAccounts.objects.filter(
            company_id=company_id,
            is_active=True
        ).order_by('account_code')
        
        # Build hierarchy
        accounts_dict = {str(acc.id): {
            'id': str(acc.id),
            'code': acc.account_code,
            'name': acc.account_name,
            'type': acc.account_type,
            'is_group': acc.is_group_account,
            'parent_id': str(acc.parent_account_id) if acc.parent_account_id else None,
            'children': []
        } for acc in accounts}
        
        # Build tree structure
        root_accounts = []
        for acc_data in accounts_dict.values():
            if acc_data['parent_id'] and acc_data['parent_id'] in accounts_dict:
                accounts_dict[acc_data['parent_id']]['children'].append(acc_data)
            else:
                root_accounts.append(acc_data)
        
        return Response({
            'total_accounts': len(accounts),
            'root_accounts': root_accounts
        })
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Get all children accounts of this account."""
        account = self.get_object()
        
        children = ChartOfAccounts.objects.filter(
            parent_account=account,
            is_active=True
        ).order_by('account_code')
        
        serializer = self.get_serializer(children, many=True)
        
        return Response({
            'parent': {
                'id': str(account.id),
                'code': account.account_code,
                'name': account.account_name
            },
            'children_count': children.count(),
            'children': serializer.data
        })

