"""
Tests for documents app models and functionality.
"""
from django.test import TestCase
from companies.models import Company
from documents.models import Document


class DocumentTest(TestCase):
    """Test Document model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            company_name="Test Corp",
            tax_id="12-3456789"
        )
        self.document = Document.objects.create(
            company=self.company,
            file_name="test.pdf",
            file_type="PDF"
        )
    
    def test_document_creation(self):
        """Test document is created correctly."""
        self.assertEqual(self.document.file_name, "test.pdf")
        self.assertEqual(self.document.file_type, "PDF")
        self.assertEqual(self.document.status, "PENDING")
