"""
Trial Balance (Balancete de Verificação) Service

Generates trial balance report showing all accounts with their debit and credit balances.
"""
from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone
from companies.models import ChartOfAccounts
from transactions.models import JournalEntryLine, JournalEntryBalance


class TrialBalanceService:
    """Service for generating trial balance reports."""
    
    @staticmethod
    def generate(company, start_date=None, end_date=None, use_snapshots=True):
        """
        Generate trial balance for a company.
        
        Args:
            company: Company object
            start_date: Start date (None = beginning of time)
            end_date: End date (None = today)
            use_snapshots: Use balance snapshots for performance
            
        Returns:
            dict: Trial balance data with accounts and totals
        """
        if end_date is None:
            end_date = timezone.now().date()
        
        # Get all active accounts
        accounts = ChartOfAccounts.objects.filter(
            company=company,
            is_active=True
        ).order_by('account_code')
        
        trial_balance_data = []
        total_debits = Decimal('0.00')
        total_credits = Decimal('0.00')
        
        for account in accounts:
            # Calculate balance for this account
            if use_snapshots:
                balance = TrialBalanceService._calculate_balance_with_snapshots(
                    company, account, start_date, end_date
                )
            else:
                balance = TrialBalanceService._calculate_balance_direct(
                    company, account, start_date, end_date
                )
            
            # Skip accounts with zero balance
            if balance == 0:
                continue
            
            # Determine debit or credit based on normal balance and actual balance
            # For assets and expenses (debit normal balance):
            #   - Positive balance = debit
            #   - Negative balance = credit
            # For liabilities, equity, revenue (credit normal balance):
            #   - Positive balance = credit
            #   - Negative balance = debit
            
            debit_amount = Decimal('0.00')
            credit_amount = Decimal('0.00')
            
            if account.normal_balance == 'debit':
                if balance >= 0:
                    debit_amount = balance
                else:
                    credit_amount = abs(balance)
            else:  # credit normal balance
                if balance >= 0:
                    credit_amount = balance
                else:
                    debit_amount = abs(balance)
            
            total_debits += debit_amount
            total_credits += credit_amount
            
            trial_balance_data.append({
                'account_code': account.account_code,
                'account_name': account.account_name,
                'account_type': account.account_type,
                'level': account.level,
                'is_group_account': account.is_group_account,
                'debit': float(debit_amount),
                'credit': float(credit_amount),
                'balance': float(balance),
            })
        
        # Check if trial balance is balanced
        is_balanced = abs(total_debits - total_credits) < Decimal('0.01')
        difference = float(total_debits - total_credits)
        
        return {
            'company': {
                'id': str(company.id),
                'name': company.name,
                'tax_id': company.tax_id,
            },
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat(),
            },
            'accounts': trial_balance_data,
            'totals': {
                'total_debits': float(total_debits),
                'total_credits': float(total_credits),
                'difference': difference,
                'is_balanced': is_balanced,
            },
            'generated_at': timezone.now().isoformat(),
        }
    
    @staticmethod
    def _calculate_balance_with_snapshots(company, account, start_date, end_date):
        """
        Calculate balance using snapshots for performance.
        
        Args:
            company: Company object
            account: ChartOfAccounts object
            start_date: Start date (None = beginning)
            end_date: End date
            
        Returns:
            Decimal: Account balance
        """
        # Try to use JournalEntryBalance manager
        try:
            balance_manager = JournalEntryBalance.objects
            end_timestamp = timezone.make_aware(
                timezone.datetime.combine(end_date, timezone.datetime.max.time())
            )
            balance = balance_manager.calculate_balance(company, account, end_timestamp)
            
            # If start_date is provided, subtract the balance at start_date
            if start_date:
                start_timestamp = timezone.make_aware(
                    timezone.datetime.combine(start_date, timezone.datetime.min.time())
                )
                start_balance = balance_manager.calculate_balance(company, account, start_timestamp)
                balance -= start_balance
            
            return balance
        except Exception:
            # Fallback to direct calculation
            return TrialBalanceService._calculate_balance_direct(
                company, account, start_date, end_date
            )
    
    @staticmethod
    def _calculate_balance_direct(company, account, start_date, end_date):
        """
        Calculate balance directly from journal entries.
        
        Args:
            company: Company object
            account: ChartOfAccounts object
            start_date: Start date (None = beginning)
            end_date: End date
            
        Returns:
            Decimal: Account balance
        """
        lines_query = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__company=company,
            journal_entry__date__lte=end_date
        )
        
        if start_date:
            lines_query = lines_query.filter(
                journal_entry__date__gte=start_date
            )
        
        aggregates = lines_query.aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        total_debit = aggregates['total_debit'] or Decimal('0.00')
        total_credit = aggregates['total_credit'] or Decimal('0.00')
        
        # Balance = credits - debits (positive = credit balance)
        return total_credit - total_debit
    
    @staticmethod
    def export_to_dict(trial_balance_data):
        """
        Export trial balance to a simple dictionary format.
        
        Args:
            trial_balance_data: Trial balance data from generate()
            
        Returns:
            dict: Simplified trial balance data
        """
        return trial_balance_data
    
    @staticmethod
    def validate_trial_balance(trial_balance_data):
        """
        Validate that trial balance is balanced.
        
        Args:
            trial_balance_data: Trial balance data from generate()
            
        Returns:
            tuple: (is_valid, error_message)
        """
        totals = trial_balance_data['totals']
        
        if not totals['is_balanced']:
            return (
                False,
                f"Trial balance is not balanced. Difference: ${totals['difference']:.2f}"
            )
        
        return (True, "Trial balance is balanced.")

