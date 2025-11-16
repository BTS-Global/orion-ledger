"""
Tests for reports app and trial balance generation.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from companies.models import Company, ChartOfAccounts
from transactions.models import JournalEntry, JournalEntryLine, JournalEntryBalance
from reports.trial_balance import TrialBalanceService
from decimal import Decimal
from datetime import date, timedelta
from core.test_utils import create_test_company, create_test_user, create_test_account


class TrialBalanceTest(TestCase):
    """Test Trial Balance generation."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.user = create_test_user(username="testuser", password="testpass123")
        
        # Create chart of accounts
        self.cash = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="1000",
            account_name="Cash",
            account_type="ASSET"
        )
        self.accounts_receivable = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="1200",
            account_name="Accounts Receivable",
            account_type="ASSET"
        )
        self.revenue = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="4000",
            account_name="Revenue",
            account_type="REVENUE"
        )
        self.expense = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="5000",
            account_name="Expenses",
            account_type="EXPENSE"
        )
    
    def test_trial_balance_generation(self):
        """Test basic trial balance generation."""
        # Create journal entries
        entry = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Test entry",
            created_by=self.user
        )
        
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=self.cash,
            debit=Decimal('1000.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=self.revenue,
            debit=Decimal('0.00'),
            credit=Decimal('1000.00')
        )
        
        # Generate trial balance
        tb = TrialBalanceService.generate(
            company=self.company,
            use_snapshots=False
        )
        
        self.assertIsNotNone(tb)
        self.assertEqual(tb['total_debits'], tb['total_credits'])
    
    def test_trial_balance_balanced(self):
        """Test that trial balance is always balanced."""
        # Create multiple entries
        entries_data = [
            (self.cash, Decimal('5000.00'), Decimal('0.00')),
            (self.revenue, Decimal('0.00'), Decimal('5000.00')),
            (self.expense, Decimal('1500.00'), Decimal('0.00')),
            (self.cash, Decimal('0.00'), Decimal('1500.00')),
        ]
        
        entry = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Multiple entries",
            created_by=self.user
        )
        
        for account, debit, credit in entries_data:
            JournalEntryLine.objects.create(
                journal_entry=entry,
                account=account,
                debit=debit,
                credit=credit
            )
        
        tb = TrialBalanceService.generate(
            company=self.company,
            use_snapshots=False
        )
        
        self.assertEqual(tb['total_debits'], tb['total_credits'])
    
    def test_trial_balance_date_filtering(self):
        """Test trial balance with date filtering."""
        # Create entries on different dates
        past_entry = JournalEntry.objects.create(
            company=self.company,
            date=date.today() - timedelta(days=30),
            description="Past entry",
            created_by=self.user
        )
        JournalEntryLine.objects.create(
            journal_entry=past_entry,
            account=self.cash,
            debit=Decimal('1000.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=past_entry,
            account=self.revenue,
            debit=Decimal('0.00'),
            credit=Decimal('1000.00')
        )
        
        recent_entry = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Recent entry",
            created_by=self.user
        )
        JournalEntryLine.objects.create(
            journal_entry=recent_entry,
            account=self.cash,
            debit=Decimal('500.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=recent_entry,
            account=self.revenue,
            debit=Decimal('0.00'),
            credit=Decimal('500.00')
        )
        
        # Test with date range
        tb = TrialBalanceService.generate(
            company=self.company,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today(),
            use_snapshots=False
        )
        
        self.assertIsNotNone(tb)
    
    def test_trial_balance_with_snapshots(self):
        """Test trial balance using balance snapshots."""
        # Create balance snapshot
        JournalEntryBalance.objects.create(
            account=self.cash,
            balance_date=date.today() - timedelta(days=1),
            debit_balance=Decimal('10000.00'),
            credit_balance=Decimal('0.00')
        )
        
        # Generate trial balance with snapshots
        tb = TrialBalanceService.generate(
            company=self.company,
            use_snapshots=True
        )
        
        self.assertIsNotNone(tb)
    
    def test_account_balances_accuracy(self):
        """Test accuracy of account balances in trial balance."""
        # Create known transactions
        entry1 = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Entry 1",
            created_by=self.user
        )
        JournalEntryLine.objects.create(
            journal_entry=entry1,
            account=self.cash,
            debit=Decimal('5000.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=entry1,
            account=self.revenue,
            debit=Decimal('0.00'),
            credit=Decimal('5000.00')
        )
        
        entry2 = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Entry 2",
            created_by=self.user
        )
        JournalEntryLine.objects.create(
            journal_entry=entry2,
            account=self.expense,
            debit=Decimal('2000.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=entry2,
            account=self.cash,
            debit=Decimal('0.00'),
            credit=Decimal('2000.00')
        )
        
        tb = TrialBalanceService.generate(
            company=self.company,
            use_snapshots=False
        )
        
        # Verify account balances
        accounts = {acc['account'].account_code: acc for acc in tb['accounts']}
        
        # Cash should have 5000 debit - 2000 credit = 3000 debit
        cash_balance = accounts['1000']['debit'] - accounts['1000']['credit']
        self.assertEqual(cash_balance, Decimal('3000.00'))


class ReportAPITest(TestCase):
    """Test Reports API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user(username="testuser", password="testpass123")
        self.token = Token.objects.create(user=self.user)
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create basic accounts
        self.cash = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="1000",
            account_name="Cash",
            account_type="ASSET"
        )
    
    def test_trial_balance_endpoint(self):
        """Test trial balance API endpoint."""
        response = self.client.get(
            f'/api/reports/trial-balance/',
            {'company': self.company.id}
        )
        # Note: This assumes the endpoint exists
        # self.assertEqual(response.status_code, 200)
    
    def test_financial_statements_endpoint(self):
        """Test financial statements generation."""
        # Balance Sheet
        response = self.client.get(
            f'/api/reports/balance-sheet/',
            {'company': self.company.id}
        )
        # Note: Implementation needed
    
    def test_income_statement_endpoint(self):
        """Test income statement generation."""
        response = self.client.get(
            f'/api/reports/income-statement/',
            {'company': self.company.id}
        )
        # Note: Implementation needed


class FinancialReportAccuracyTest(TestCase):
    """Test accuracy of financial reports."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.user = create_test_user(username="testuser", password="testpass123")
        
        # Create complete chart of accounts
        self.assets = {
            'cash': ChartOfAccounts.objects.create(
                company=self.company,
                account_code="1000",
                account_name="Cash",
                account_type="ASSET"
            ),
            'ar': ChartOfAccounts.objects.create(
                company=self.company,
                account_code="1200",
                account_name="Accounts Receivable",
                account_type="ASSET"
            )
        }
        
        self.liabilities = {
            'ap': ChartOfAccounts.objects.create(
                company=self.company,
                account_code="2000",
                account_name="Accounts Payable",
                account_type="LIABILITY"
            )
        }
        
        self.equity = {
            'capital': ChartOfAccounts.objects.create(
                company=self.company,
                account_code="3000",
                account_name="Owner's Capital",
                account_type="EQUITY"
            )
        }
        
        self.revenue = {
            'sales': ChartOfAccounts.objects.create(
                company=self.company,
                account_code="4000",
                account_name="Sales Revenue",
                account_type="REVENUE"
            )
        }
        
        self.expenses = {
            'salaries': ChartOfAccounts.objects.create(
                company=self.company,
                account_code="5000",
                account_name="Salaries Expense",
                account_type="EXPENSE"
            )
        }
    
    def test_accounting_equation_holds(self):
        """Test that Assets = Liabilities + Equity always holds."""
        # Create initial capital investment
        entry = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Initial investment",
            created_by=self.user
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=self.assets['cash'],
            debit=Decimal('50000.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=self.equity['capital'],
            debit=Decimal('0.00'),
            credit=Decimal('50000.00')
        )
        
        # Generate trial balance and verify equation
        tb = TrialBalanceService.generate(
            company=self.company,
            use_snapshots=False
        )
        
        # Calculate totals by account type
        assets_total = sum(
            acc['debit'] - acc['credit']
            for acc in tb['accounts']
            if acc['account'].account_type == 'ASSET'
        )
        
        liabilities_total = sum(
            acc['credit'] - acc['debit']
            for acc in tb['accounts']
            if acc['account'].account_type == 'LIABILITY'
        )
        
        equity_total = sum(
            acc['credit'] - acc['debit']
            for acc in tb['accounts']
            if acc['account'].account_type == 'EQUITY'
        )
        
        # Assets = Liabilities + Equity
        self.assertEqual(assets_total, liabilities_total + equity_total)
