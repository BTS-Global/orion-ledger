"""
Tests for transactions app models and functionality.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from companies.models import Company
from transactions.models import Transaction, JournalEntry
from decimal import Decimal
from datetime import date


class TransactionTest(TestCase):
    """Test Transaction model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            company_name="Test Corp",
            tax_id="12-3456789"
        )
        self.transaction = Transaction.objects.create(
            company=self.company,
            date=date.today(),
            description="Test transaction",
            amount=Decimal('1000.00'),
            category="REVENUE"
        )
    
    def test_transaction_creation(self):
        """Test transaction is created correctly."""
        self.assertEqual(self.transaction.description, "Test transaction")
        self.assertEqual(self.transaction.amount, Decimal('1000.00'))
        self.assertEqual(self.transaction.category, "REVENUE")
    
    def test_transaction_status(self):
        """Test transaction default status."""
        self.assertEqual(self.transaction.status, "PENDING")


class JournalEntryTest(TestCase):
    """Test Journal Entry model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            company_name="Test Corp",
            tax_id="12-3456789"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
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
