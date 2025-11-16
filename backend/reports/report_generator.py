"""
Optimized reporting service with caching and performance improvements.
"""
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.db.models import Sum, Q, F
from django.utils import timezone

from companies.models import Company, ChartOfAccounts
from transactions.models import Transaction, JournalEntry
from core.cache_service import AccountingCache, QueryOptimizer, PerformanceMonitor


class ReportGenerator:
    """Generate financial reports with caching and optimization."""
    
    def __init__(self, company: Company):
        self.company = company
    
    def generate_trial_balance(self, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict:
        """
        Generate trial balance report with caching.
        
        Args:
            start_date: Start date for report period
            end_date: End date for report period
            
        Returns:
            dict: Trial balance data
        """
        # Set default dates if not provided
        if not end_date:
            end_date = timezone.now()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Check cache first
        cached = AccountingCache.get_trial_balance(
            str(self.company.id), start_str, end_str
        )
        if cached:
            return cached
        
        # Generate report
        accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            is_active=True
        ).order_by('account_code')
        
        report_data = {
            'company': self.company.name,
            'period_start': start_str,
            'period_end': end_str,
            'generated_at': timezone.now().isoformat(),
            'accounts': [],
            'totals': {
                'debits': Decimal('0.00'),
                'credits': Decimal('0.00')
            }
        }
        
        for account in accounts:
            # Calculate account balance for period
            balance_data = self._calculate_account_balance(
                account, start_date, end_date
            )
            
            if balance_data['balance'] != Decimal('0.00'):
                report_data['accounts'].append(balance_data)
                
                # Update totals
                if balance_data['balance'] > 0:
                    if account.account_type in ['ASSET', 'EXPENSE']:
                        report_data['totals']['debits'] += balance_data['balance']
                    else:
                        report_data['totals']['credits'] += balance_data['balance']
                else:
                    if account.account_type in ['ASSET', 'EXPENSE']:
                        report_data['totals']['credits'] += abs(balance_data['balance'])
                    else:
                        report_data['totals']['debits'] += abs(balance_data['balance'])
        
        # Cache the result
        AccountingCache.set_trial_balance(
            str(self.company.id), start_str, end_str, report_data
        )
        
        return report_data
    
    def _calculate_account_balance(self, account: ChartOfAccounts,
                                   start_date: datetime,
                                   end_date: datetime) -> Dict:
        """Calculate account balance for a period."""
        # Get transactions for this account in the period
        transactions = Transaction.objects.filter(
            account=account,
            company=self.company,
            date__gte=start_date,
            date__lte=end_date,
            is_validated=True
        )
        
        debits = transactions.filter(type='DEBIT').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        credits = transactions.filter(type='CREDIT').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Calculate balance based on account type
        if account.account_type in ['ASSET', 'EXPENSE']:
            balance = debits - credits
        else:  # LIABILITY, EQUITY, REVENUE
            balance = credits - debits
        
        return {
            'account_code': account.account_code,
            'account_name': account.account_name,
            'account_type': account.account_type,
            'debits': float(debits),
            'credits': float(credits),
            'balance': float(balance)
        }
    
    def generate_profit_loss(self, start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> Dict:
        """
        Generate Profit & Loss (Income Statement) report.
        
        Args:
            start_date: Start date for report period
            end_date: End date for report period
            
        Returns:
            dict: P&L data
        """
        if not end_date:
            end_date = timezone.now()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        # Get revenue and expense accounts
        revenue_accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            account_type='REVENUE',
            is_active=True
        )
        
        expense_accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            account_type='EXPENSE',
            is_active=True
        )
        
        report = {
            'company': self.company.name,
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date.strftime('%Y-%m-%d'),
            'generated_at': timezone.now().isoformat(),
            'revenue': [],
            'expenses': [],
            'total_revenue': Decimal('0.00'),
            'total_expenses': Decimal('0.00'),
            'net_income': Decimal('0.00')
        }
        
        # Calculate revenues
        for account in revenue_accounts:
            balance = self._calculate_account_balance(
                account, start_date, end_date
            )
            if balance['balance'] != 0:
                report['revenue'].append(balance)
                report['total_revenue'] += Decimal(str(balance['balance']))
        
        # Calculate expenses
        for account in expense_accounts:
            balance = self._calculate_account_balance(
                account, start_date, end_date
            )
            if balance['balance'] != 0:
                report['expenses'].append(balance)
                report['total_expenses'] += Decimal(str(balance['balance']))
        
        # Calculate net income
        report['net_income'] = report['total_revenue'] - report['total_expenses']
        
        # Convert Decimals to floats for JSON serialization
        report['total_revenue'] = float(report['total_revenue'])
        report['total_expenses'] = float(report['total_expenses'])
        report['net_income'] = float(report['net_income'])
        
        return report
    
    def generate_balance_sheet(self, as_of_date: Optional[datetime] = None) -> Dict:
        """
        Generate Balance Sheet report.
        
        Args:
            as_of_date: Date for balance sheet snapshot
            
        Returns:
            dict: Balance sheet data
        """
        if not as_of_date:
            as_of_date = timezone.now()
        
        start_date = datetime(2000, 1, 1)  # Beginning of time
        
        report = {
            'company': self.company.name,
            'as_of_date': as_of_date.strftime('%Y-%m-%d'),
            'generated_at': timezone.now().isoformat(),
            'assets': {
                'current_assets': [],
                'fixed_assets': [],
                'total': Decimal('0.00')
            },
            'liabilities': {
                'current_liabilities': [],
                'long_term_liabilities': [],
                'total': Decimal('0.00')
            },
            'equity': {
                'accounts': [],
                'total': Decimal('0.00')
            }
        }
        
        # Get all balance sheet accounts
        asset_accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            account_type='ASSET',
            is_active=True
        )
        
        liability_accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            account_type='LIABILITY',
            is_active=True
        )
        
        equity_accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            account_type='EQUITY',
            is_active=True
        )
        
        # Calculate assets
        for account in asset_accounts:
            balance = self._calculate_account_balance(
                account, start_date, as_of_date
            )
            if balance['balance'] != 0:
                # Categorize as current or fixed based on account code
                if account.account_code.startswith('11'):
                    report['assets']['current_assets'].append(balance)
                else:
                    report['assets']['fixed_assets'].append(balance)
                report['assets']['total'] += Decimal(str(balance['balance']))
        
        # Calculate liabilities
        for account in liability_accounts:
            balance = self._calculate_account_balance(
                account, start_date, as_of_date
            )
            if balance['balance'] != 0:
                # Categorize as current or long-term based on account code
                if account.account_code.startswith('21'):
                    report['liabilities']['current_liabilities'].append(balance)
                else:
                    report['liabilities']['long_term_liabilities'].append(balance)
                report['liabilities']['total'] += Decimal(str(balance['balance']))
        
        # Calculate equity
        for account in equity_accounts:
            balance = self._calculate_account_balance(
                account, start_date, as_of_date
            )
            if balance['balance'] != 0:
                report['equity']['accounts'].append(balance)
                report['equity']['total'] += Decimal(str(balance['balance']))
        
        # Convert Decimals to floats
        report['assets']['total'] = float(report['assets']['total'])
        report['liabilities']['total'] = float(report['liabilities']['total'])
        report['equity']['total'] = float(report['equity']['total'])
        
        return report
    
    def generate_cash_flow(self, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict:
        """
        Generate simple Cash Flow report.
        
        Args:
            start_date: Start date for report period
            end_date: End date for report period
            
        Returns:
            dict: Cash flow data
        """
        if not end_date:
            end_date = timezone.now()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        # Get cash and cash equivalent accounts (typically 1110)
        cash_accounts = ChartOfAccounts.objects.filter(
            company=self.company,
            account_code__startswith='111',
            is_active=True
        )
        
        report = {
            'company': self.company.name,
            'period_start': start_date.strftime('%Y-%m-%d'),
            'period_end': end_date.strftime('%Y-%m-%d'),
            'generated_at': timezone.now().isoformat(),
            'beginning_balance': Decimal('0.00'),
            'cash_inflows': Decimal('0.00'),
            'cash_outflows': Decimal('0.00'),
            'net_change': Decimal('0.00'),
            'ending_balance': Decimal('0.00'),
            'transactions': []
        }
        
        for account in cash_accounts:
            # Get beginning balance
            beginning = self._calculate_account_balance(
                account, datetime(2000, 1, 1), start_date
            )
            report['beginning_balance'] += Decimal(str(beginning['balance']))
            
            # Get transactions in period
            transactions = Transaction.objects.filter(
                account=account,
                company=self.company,
                date__gte=start_date,
                date__lte=end_date,
                is_validated=True
            ).order_by('date')
            
            for trans in transactions:
                trans_data = {
                    'date': trans.date.strftime('%Y-%m-%d'),
                    'description': trans.description,
                    'amount': float(trans.amount),
                    'type': trans.type
                }
                report['transactions'].append(trans_data)
                
                if trans.type == 'DEBIT':
                    report['cash_inflows'] += trans.amount
                else:
                    report['cash_outflows'] += trans.amount
        
        report['net_change'] = report['cash_inflows'] - report['cash_outflows']
        report['ending_balance'] = report['beginning_balance'] + report['net_change']
        
        # Convert Decimals to floats
        report['beginning_balance'] = float(report['beginning_balance'])
        report['cash_inflows'] = float(report['cash_inflows'])
        report['cash_outflows'] = float(report['cash_outflows'])
        report['net_change'] = float(report['net_change'])
        report['ending_balance'] = float(report['ending_balance'])
        
        return report
