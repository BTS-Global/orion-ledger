"""
Tests for offshore compliance and reporting.
"""
from django.test import TestCase
from companies.models import Company
from offshore.models import AnnualReturn, EconomicSubstanceReport, JurisdictionFee
from datetime import date
from core.test_utils import create_test_company
from decimal import Decimal


class AnnualReturnTest(TestCase):
    """Test Annual Return filing."""
    
    def setUp(self):
        self.company = create_test_company(jurisdiction='BVI')
    
    def test_annual_return_creation(self):
        """Test annual return creation."""
        annual_return = AnnualReturn.objects.create(
            company=self.company,
            filing_year=2024,
            due_date=date(2024, 12, 31),
            status="PENDING"
        )
        
        self.assertEqual(annual_return.filing_year, 2024)
        self.assertEqual(annual_return.status, "PENDING")


class EconomicSubstanceReportTest(TestCase):
    """Test Economic Substance Reporting."""
    
    def setUp(self):
        self.company = create_test_company(jurisdiction='BVI')
    
    def test_esr_creation(self):
        """Test ESR creation."""
        esr = EconomicSubstanceReport.objects.create(
            company=self.company,
            reporting_year=2024,
            activity_type="HOLDING",
            has_substance=True,
            gross_income=Decimal('1000000.00'),
            number_of_employees=5,
            operating_expenditure=Decimal('250000.00')
        )
        
        self.assertEqual(esr.reporting_year, 2024)
        self.assertTrue(esr.has_substance)
        self.assertEqual(esr.number_of_employees, 5)


class JurisdictionFeeTest(TestCase):
    """Test jurisdiction fee tracking."""
    
    def test_fee_creation(self):
        """Test creating jurisdiction fee."""
        fee = JurisdictionFee.objects.create(
            jurisdiction='BVI',
            fee_type='ANNUAL_RETURN',
            amount=Decimal('350.00'),
            currency='USD',
            effective_from=date(2024, 1, 1)
        )
        
        self.assertEqual(fee.jurisdiction, 'BVI')
        self.assertEqual(fee.amount, Decimal('350.00'))
