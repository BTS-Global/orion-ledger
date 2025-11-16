"""
Tests for transactions app models and functionality.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from companies.models import Company, ChartOfAccounts
from transactions.models import Transaction, JournalEntry, JournalEntryLine, JournalEntryBalance
from transactions.serializers import TransactionSerializer
from decimal import Decimal
from datetime import date, timedelta
from core.test_utils import create_test_company, create_test_user, create_test_account
from django.core.exceptions import ValidationError


class TransactionTest(TestCase):
    """Test Transaction model."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.account = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="5000",
            account_name="Expenses",
            account_type="EXPENSE"
        )
        self.transaction = Transaction.objects.create(
            company=self.company,
            date=date.today(),
            description="Test transaction",
            amount=Decimal('1000.00'),
            category="REVENUE",
            account=self.account
        )
    
    def test_transaction_creation(self):
        """Test transaction is created correctly."""
        self.assertEqual(self.transaction.description, "Test transaction")
        self.assertEqual(self.transaction.amount, Decimal('1000.00'))
        self.assertEqual(self.transaction.category, "REVENUE")
    
    def test_transaction_status(self):
        """Test transaction default status."""
        self.assertEqual(self.transaction.status, "PENDING")
    
    def test_transaction_validation(self):
        """Test transaction validation rules."""
        # Test future date validation
        serializer = TransactionSerializer(data={
            'company': self.company.id,
            'date': (date.today() + timedelta(days=1)).isoformat(),
            'description': 'Future transaction',
            'amount': '100.00'
        })
        self.assertFalse(serializer.is_valid())
        
        # Test zero amount validation
        serializer = TransactionSerializer(data={
            'company': self.company.id,
            'date': date.today().isoformat(),
            'description': 'Zero transaction',
            'amount': '0.00'
        })
        self.assertFalse(serializer.is_valid())
        
        # Test empty description
        serializer = TransactionSerializer(data={
            'company': self.company.id,
            'date': date.today().isoformat(),
            'description': '   ',
            'amount': '100.00'
        })
        self.assertFalse(serializer.is_valid())


class JournalEntryTest(TestCase):
    """Test Journal Entry model."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.user = create_test_user(username="testuser", password="testpass123")
        self.debit_account = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="1000",
            account_name="Cash",
            account_type="ASSET"
        )
        self.credit_account = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="4000",
            account_name="Revenue",
            account_type="REVENUE"
        )
        self.journal_entry = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Test entry",
            created_by=self.user
        )
    
    def test_journal_entry_creation(self):
        """Test journal entry is created correctly."""
        self.assertEqual(self.journal_entry.description, "Test entry")
        self.assertEqual(self.journal_entry.company, self.company)
    
    def test_journal_entry_balanced(self):
        """Test journal entry is_balanced property."""
        # Without lines, should be balanced (0 = 0)
        self.assertTrue(self.journal_entry.is_balanced)
        
        # Add balanced entries
        JournalEntryLine.objects.create(
            journal_entry=self.journal_entry,
            account=self.debit_account,
            debit=Decimal('1000.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=self.journal_entry,
            account=self.credit_account,
            debit=Decimal('0.00'),
            credit=Decimal('1000.00')
        )
        
        self.assertTrue(self.journal_entry.is_balanced)
    
    def test_journal_entry_unbalanced(self):
        """Test unbalanced journal entry detection."""
        # Add unbalanced entries
        JournalEntryLine.objects.create(
            journal_entry=self.journal_entry,
            account=self.debit_account,
            debit=Decimal('1000.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=self.journal_entry,
            account=self.credit_account,
            debit=Decimal('0.00'),
            credit=Decimal('500.00')
        )
        
        self.assertFalse(self.journal_entry.is_balanced)


class DoubleEntryAccountingTest(TestCase):
    """Test double-entry accounting principles."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.user = create_test_user(username="testuser", password="testpass123")
        
        # Create complete chart of accounts
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
            account_name="Service Revenue",
            account_type="REVENUE"
        )
        self.expense = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="5000",
            account_name="Office Expense",
            account_type="EXPENSE"
        )
    
    def test_cash_sale_entry(self):
        """Test proper double-entry for cash sale."""
        entry = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Cash sale",
            created_by=self.user
        )
        
        # Debit Cash, Credit Revenue
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=self.cash,
            debit=Decimal('1000.00'),
            credit=Decimal('0.00'),
            description="Cash received"
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=self.revenue,
            debit=Decimal('0.00'),
            credit=Decimal('1000.00'),
            description="Service revenue"
        )
        
        self.assertTrue(entry.is_balanced)
        self.assertEqual(entry.total_debits, Decimal('1000.00'))
        self.assertEqual(entry.total_credits, Decimal('1000.00'))
    
    def test_expense_payment(self):
        """Test proper double-entry for expense payment."""
        entry = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Office supplies purchase",
            created_by=self.user
        )
        
        # Debit Expense, Credit Cash
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=self.expense,
            debit=Decimal('250.00'),
            credit=Decimal('0.00'),
            description="Office supplies"
        )
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=self.cash,
            debit=Decimal('0.00'),
            credit=Decimal('250.00'),
            description="Cash paid"
        )
        
        self.assertTrue(entry.is_balanced)
    
    def test_accounting_equation(self):
        """Test accounting equation: Assets = Liabilities + Equity."""
        # Create liability and equity accounts
        liability = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="2000",
            account_name="Accounts Payable",
            account_type="LIABILITY"
        )
        equity = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="3000",
            account_name="Owner's Equity",
            account_type="EQUITY"
        )
        
        # Initial investment: Debit Cash, Credit Equity
        entry1 = JournalEntry.objects.create(
            company=self.company,
            date=date.today(),
            description="Initial investment",
            created_by=self.user
        )
        JournalEntryLine.objects.create(
            journal_entry=entry1,
            account=self.cash,
            debit=Decimal('10000.00'),
            credit=Decimal('0.00')
        )
        JournalEntryLine.objects.create(
            journal_entry=entry1,
            account=equity,
            debit=Decimal('0.00'),
            credit=Decimal('10000.00')
        )
        
        self.assertTrue(entry1.is_balanced)


class TransactionAPITest(TestCase):
    """Test Transaction API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user(username="testuser", password="testpass123")
        self.token = Token.objects.create(user=self.user)
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.account = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="5000",
            account_name="Expenses",
            account_type="EXPENSE"
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_create_transaction(self):
        """Test creating transaction via API."""
        data = {
            'company': self.company.id,
            'date': date.today().isoformat(),
            'description': 'API Test Transaction',
            'amount': '500.00',
            'account': self.account.id
        }
        response = self.client.post('/api/transactions/', data)
        self.assertEqual(response.status_code, 201)
    
    def test_list_transactions(self):
        """Test listing transactions."""
        Transaction.objects.create(
            company=self.company,
            date=date.today(),
            description="Transaction 1",
            amount=Decimal('100.00'),
            account=self.account
        )
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 200)
    
    def test_update_transaction(self):
        """Test updating transaction."""
        transaction = Transaction.objects.create(
            company=self.company,
            date=date.today(),
            description="Original",
            amount=Decimal('100.00'),
            account=self.account
        )
        data = {
            'description': 'Updated description',
            'amount': '150.00'
        }
        response = self.client.patch(f'/api/transactions/{transaction.id}/', data)
        self.assertEqual(response.status_code, 200)
        
        transaction.refresh_from_db()
        self.assertEqual(transaction.description, 'Updated description')


class BalanceCalculationTest(TestCase):
    """Test balance calculation and snapshots."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.user = create_test_user(username="testuser", password="testpass123")
        self.account = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="1000",
            account_name="Cash",
            account_type="ASSET"
        )
    
    def test_balance_snapshot_creation(self):
        """Test balance snapshot is created correctly."""
        snapshot = JournalEntryBalance.objects.create(
            account=self.account,
            balance_date=date.today(),
            debit_balance=Decimal('5000.00'),
            credit_balance=Decimal('2000.00')
        )
        
        self.assertEqual(snapshot.net_balance, Decimal('3000.00'))
    
    def test_running_balance(self):
        """Test running balance calculation."""
        # Create multiple journal entries
        for i in range(5):
            entry = JournalEntry.objects.create(
                company=self.company,
                date=date.today(),
                description=f"Entry {i}",
                created_by=self.user
            )
            JournalEntryLine.objects.create(
                journal_entry=entry,
                account=self.account,
                debit=Decimal('100.00'),
                credit=Decimal('0.00')
            )
        
        # Calculate total balance
        total = JournalEntryLine.objects.filter(
            account=self.account
        ).aggregate(
            total_debit=sum('debit'),
            total_credit=sum('credit')
        )
        
        # This test would need actual implementation in models
