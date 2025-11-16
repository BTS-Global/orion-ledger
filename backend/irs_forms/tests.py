"""
Tests for irs_forms app models and functionality.
"""
from django.test import TestCase
from companies.models import Company
from irs_forms.models import IRSForm


class IRSFormTest(TestCase):
    """Test IRS Form model."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.irs_form = IRSForm.objects.create(
            company=self.company,
            form_type="1120",
            tax_year=2024,
            form_data={"test": "data"}
        )
    
    def test_irs_form_creation(self):
        """Test IRS form is created correctly."""
        self.assertEqual(self.irs_form.form_type, "1120")
        self.assertEqual(self.irs_form.tax_year, 2024)
        self.assertEqual(self.irs_form.status, "DRAFT")
    
    def test_irs_form_unique_constraint(self):
        """Test unique constraint on company, form_type, tax_year."""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            IRSForm.objects.create(
                company=self.company,
                form_type="1120",
                tax_year=2024
            )
