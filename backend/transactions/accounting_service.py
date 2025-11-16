"""
Accounting service for double-entry bookkeeping and financial calculations.
"""
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Tuple
from django.db.models import Sum, Q
from django.utils import timezone

from .models import Transaction, JournalEntry, JournalEntryLine
from companies.models import ChartOfAccounts


class AccountingService:
    """Service for accounting operations and financial calculations."""
    
    def __init__(self, company):
        self.company = company
    
    @staticmethod
    def create_journal_entry_from_transaction(transaction: Transaction) -> JournalEntry:
        """
        Create a double-entry journal entry from a validated transaction.
        
        Args:
            transaction: Validated Transaction object
            
        Returns:
            JournalEntry object
        """
        if not transaction.is_validated or not transaction.account:
            raise ValueError("Transaction must be validated and have an account assigned")
        
        # Create journal entry
        entry = JournalEntry.objects.create(
            company=transaction.company,
            date=transaction.date,
            description=transaction.description,
            reference=f"TRX-{transaction.id}",
            created_by=transaction.validated_by
        )
        
        # Determine debit and credit based on account type and amount
        account = transaction.account
        amount = abs(transaction.amount)
        
        # Default contra account (can be customized)
        # For now, use a generic "Cash" or "Bank" account
        contra_account = AccountingService._get_default_contra_account(transaction.company, account.account_type)
        
        if transaction.amount > 0:
            # Positive amount = money in
            if account.account_type in ['ASSET', 'EXPENSE']:
                # Debit the account (increase)
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=amount,
                    credit=Decimal('0')
                )
                # Credit contra account
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=contra_account,
                    debit=Decimal('0'),
                    credit=amount
                )
            else:  # REVENUE, LIABILITY, EQUITY
                # Credit the account (increase)
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=Decimal('0'),
                    credit=amount
                )
                # Debit contra account
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=contra_account,
                    debit=amount,
                    credit=Decimal('0')
                )
        else:
            # Negative amount = money out
            if account.account_type in ['ASSET', 'EXPENSE']:
                # Credit the account (decrease)
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=Decimal('0'),
                    credit=amount
                )
                # Debit contra account
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=contra_account,
                    debit=amount,
                    credit=Decimal('0')
                )
            else:  # REVENUE, LIABILITY, EQUITY
                # Debit the account (decrease)
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=amount,
                    credit=Decimal('0')
                )
                # Credit contra account
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=contra_account,
                    debit=Decimal('0'),
                    credit=amount
                )
        
        return entry
    
    @staticmethod
    def _get_default_contra_account(company, account_type: str) -> ChartOfAccounts:
        """Get default contra account based on account type."""
        # Try to find a Cash or Bank account
        contra = ChartOfAccounts.objects.filter(
            company=company,
            account_type='ASSET',
            account_name__icontains='cash'
        ).first()
        
        if not contra:
            # Fallback to any asset account
            contra = ChartOfAccounts.objects.filter(
                company=company,
                account_type='ASSET'
            ).first()
        
        if not contra:
            raise ValueError("No contra account found. Please create a Cash or Bank account.")
        
        return contra
    
    def calculate_account_balance(
        self, 
        account: ChartOfAccounts, 
        start_date: date = None, 
        end_date: date = None
    ) -> Decimal:
        """
        Calculate balance for an account within a date range.
        
        Args:
            account: ChartOfAccounts object
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Account balance as Decimal
        """
        # Get all journal entry lines for this account
        lines = JournalEntryLine.objects.filter(account=account)
        
        # Filter by date range if provided
        if start_date:
            lines = lines.filter(journal_entry__date__gte=start_date)
        if end_date:
            lines = lines.filter(journal_entry__date__lte=end_date)
        
        # Calculate total debits and credits
        totals = lines.aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        total_debit = totals['total_debit'] or Decimal('0')
        total_credit = totals['total_credit'] or Decimal('0')
        
        # Calculate balance based on account type
        # Assets and Expenses: Debit increases, Credit decreases
        # Liabilities, Equity, Revenue: Credit increases, Debit decreases
        if account.account_type in ['ASSET', 'EXPENSE']:
            balance = total_debit - total_credit
        else:  # REVENUE, LIABILITY, EQUITY
            balance = total_credit - total_debit
        
        return balance
    
    def get_trial_balance(self, end_date: date = None) -> List[Dict]:
        """
        Generate trial balance for all accounts.
        
        Args:
            end_date: End date (inclusive), defaults to today
            
        Returns:
            List of dicts with account info and balances
        """
        if not end_date:
            end_date = timezone.now().date()
        
        accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            is_active=True
        ).order_by('account_code')
        
        trial_balance = []
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        
        for account in accounts:
            balance = self.calculate_account_balance(account, end_date=end_date)
            
            # Determine debit or credit balance
            if account.account_type in ['ASSET', 'EXPENSE']:
                debit_balance = balance if balance > 0 else Decimal('0')
                credit_balance = abs(balance) if balance < 0 else Decimal('0')
            else:
                credit_balance = balance if balance > 0 else Decimal('0')
                debit_balance = abs(balance) if balance < 0 else Decimal('0')
            
            total_debit += debit_balance
            total_credit += credit_balance
            
            trial_balance.append({
                'account_code': account.account_code,
                'account_name': account.account_name,
                'account_type': account.account_type,
                'debit': float(debit_balance),
                'credit': float(credit_balance),
                'balance': float(balance)
            })
        
        # Add totals
        trial_balance.append({
            'account_code': '',
            'account_name': 'TOTAL',
            'account_type': '',
            'debit': float(total_debit),
            'credit': float(total_credit),
            'balance': float(total_debit - total_credit)
        })
        
        return trial_balance
    
    def get_balance_sheet(self, end_date: date = None) -> Dict:
        """
        Generate Balance Sheet (Statement of Financial Position).
        
        Args:
            end_date: End date (inclusive), defaults to today
            
        Returns:
            Dict with assets, liabilities, and equity
        """
        if not end_date:
            end_date = timezone.now().date()
        
        accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            is_active=True
        ).order_by('account_code')
        
        assets = []
        liabilities = []
        equity = []
        
        total_assets = Decimal('0')
        total_liabilities = Decimal('0')
        total_equity = Decimal('0')
        
        for account in accounts:
            balance = self.calculate_account_balance(account, end_date=end_date)
            
            if balance == 0:
                continue
            
            account_data = {
                'account_code': account.account_code,
                'account_name': account.account_name,
                'balance': float(balance)
            }
            
            if account.account_type == 'ASSET':
                assets.append(account_data)
                total_assets += balance
            elif account.account_type == 'LIABILITY':
                liabilities.append(account_data)
                total_liabilities += balance
            elif account.account_type == 'EQUITY':
                equity.append(account_data)
                total_equity += balance
        
        # Calculate net income and add to equity
        net_income = self.calculate_net_income(end_date=end_date)
        if net_income != 0:
            equity.append({
                'account_code': '',
                'account_name': 'Net Income (Current Period)',
                'balance': float(net_income)
            })
            total_equity += net_income
        
        return {
            'date': end_date.isoformat(),
            'company': self.company.name,
            'assets': {
                'items': assets,
                'total': float(total_assets)
            },
            'liabilities': {
                'items': liabilities,
                'total': float(total_liabilities)
            },
            'equity': {
                'items': equity,
                'total': float(total_equity)
            },
            'total_liabilities_and_equity': float(total_liabilities + total_equity),
            'balanced': abs(total_assets - (total_liabilities + total_equity)) < Decimal('0.01')
        }
    
    def get_income_statement(
        self, 
        start_date: date = None, 
        end_date: date = None
    ) -> Dict:
        """
        Generate Income Statement (Profit & Loss).
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive), defaults to today
            
        Returns:
            Dict with revenues, expenses, and net income
        """
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            # Default to beginning of current year
            start_date = date(end_date.year, 1, 1)
        
        accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            is_active=True
        ).order_by('account_code')
        
        revenues = []
        expenses = []
        
        total_revenue = Decimal('0')
        total_expenses = Decimal('0')
        
        for account in accounts:
            balance = self.calculate_account_balance(
                account, 
                start_date=start_date, 
                end_date=end_date
            )
            
            if balance == 0:
                continue
            
            account_data = {
                'account_code': account.account_code,
                'account_name': account.account_name,
                'amount': float(balance)
            }
            
            if account.account_type == 'REVENUE':
                revenues.append(account_data)
                total_revenue += balance
            elif account.account_type == 'EXPENSE':
                expenses.append(account_data)
                total_expenses += balance
        
        net_income = total_revenue - total_expenses
        
        return {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'company': self.company.name,
            'revenues': {
                'items': revenues,
                'total': float(total_revenue)
            },
            'expenses': {
                'items': expenses,
                'total': float(total_expenses)
            },
            'net_income': float(net_income)
        }
    
    def calculate_net_income(
        self, 
        start_date: date = None, 
        end_date: date = None
    ) -> Decimal:
        """Calculate net income for a period."""
        income_statement = self.get_income_statement(start_date, end_date)
        return Decimal(str(income_statement['net_income']))
    
    def get_cash_flow_statement(
        self, 
        start_date: date = None, 
        end_date: date = None
    ) -> Dict:
        """
        Generate Cash Flow Statement (simplified version).
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive), defaults to today
            
        Returns:
            Dict with cash flows from operations, investing, and financing
        """
        if not end_date:
            end_date = timezone.now().date()
        if not start_date:
            start_date = date(end_date.year, 1, 1)
        
        # Get cash/bank accounts
        cash_accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            account_type='ASSET',
            is_active=True
        ).filter(
            Q(account_name__icontains='cash') | 
            Q(account_name__icontains='bank')
        )
        
        beginning_balance = Decimal('0')
        ending_balance = Decimal('0')
        
        for account in cash_accounts:
            # Calculate beginning balance (day before start_date)
            if start_date:
                from datetime import timedelta
                day_before = start_date - timedelta(days=1)
                beginning_balance += self.calculate_account_balance(
                    account, 
                    end_date=day_before
                )
            
            # Calculate ending balance
            ending_balance += self.calculate_account_balance(
                account, 
                end_date=end_date
            )
        
        # Net change in cash
        net_change = ending_balance - beginning_balance
        
        # Get net income
        net_income = self.calculate_net_income(start_date, end_date)
        
        return {
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat(),
            'company': self.company.name,
            'beginning_cash_balance': float(beginning_balance),
            'ending_cash_balance': float(ending_balance),
            'net_change_in_cash': float(net_change),
            'net_income': float(net_income),
            'operating_activities': float(net_income),  # Simplified
            'investing_activities': 0.0,  # Placeholder
            'financing_activities': 0.0,  # Placeholder
        }

