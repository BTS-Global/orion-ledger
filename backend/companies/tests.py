"""
Tests for companies app models and functionality.
"""
from django.test import TestCase
from companies.models import Company, ChartOfAccounts
from decimal import Decimal


class CompanyModelTest(TestCase):
    """Test Company model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            company_name="Test Corp",
            tax_id="12-3456789",
            fiscal_year_end="12-31",
            entity_type="LLC"
        )
    
    def test_company_creation(self):
        """Test company is created correctly."""
        self.assertEqual(self.company.company_name, "Test Corp")
        self.assertEqual(self.company.tax_id, "12-3456789")
        self.assertEqual(self.company.entity_type, "LLC")
    
    def test_company_str(self):
        """Test company string representation."""
        self.assertEqual(str(self.company), "Test Corp")


class ChartOfAccountsTest(TestCase):
    """Test Chart of Accounts model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            company_name="Test Corp",
            tax_id="12-3456789"
        )
        self.account = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="1000",
            account_name="Cash",
            account_type="ASSET"
        )
    
    def test_account_creation(self):
        """Test account is created correctly."""
        self.assertEqual(self.account.account_code, "1000")
        self.assertEqual(self.account.account_name, "Cash")
        self.assertEqual(self.account.account_type, "ASSET")
    
    def test_account_balance(self):
        """Test account balance calculation."""
        # Initially zero
        self.assertEqual(self.account.balance, Decimal('0'))


class AccountingServiceTest(TestCase):
    """Test accounting service functions."""
    
    def setUp(self):
        self.company = Company.objects.create(
            company_name="Test Corp",
            tax_id="12-3456789"
        )
        
        # Create accounts
        self.cash = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="1000",
            account_name="Cash",
            account_type="ASSET"
        )
        
        self.revenue = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="4000",
            account_name="Revenue",
            account_type="REVENUE"
        )
    
    def test_account_types(self):
        """Test account types are correct."""
        self.assertEqual(self.cash.account_type, "ASSET")
        self.assertEqual(self.revenue.account_type, "REVENUE")
