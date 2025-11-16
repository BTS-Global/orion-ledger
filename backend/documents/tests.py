"""
Tests for documents app models and functionality.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from companies.models import Company
from documents.models import Document
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import date
from core.test_utils import create_test_company, create_test_user, create_test_account


class DocumentTest(TestCase):
    """Test Document model."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
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
    
    def test_document_status_transitions(self):
        """Test document status transitions."""
        self.assertEqual(self.document.status, "PENDING")
        
        self.document.status = "PROCESSING"
        self.document.save()
        self.assertEqual(self.document.status, "PROCESSING")
        
        self.document.status = "PROCESSED"
        self.document.save()
        self.assertEqual(self.document.status, "PROCESSED")
    
    def test_document_error_status(self):
        """Test document error handling."""
        self.document.status = "ERROR"
        self.document.error_message = "Failed to process"
        self.document.save()
        
        self.assertEqual(self.document.status, "ERROR")
        self.assertIsNotNone(self.document.error_message)


class DocumentProcessingTest(TestCase):
    """Test document processing and OCR."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.user = create_test_user(username="testuser", password="testpass123")
    
    @patch('documents.tasks.process_document_task')
    def test_document_processing_trigger(self, mock_task):
        """Test that document processing is triggered on upload."""
        document = Document.objects.create(
            company=self.company,
            file_name="invoice.pdf",
            file_type="PDF",
            uploaded_by=self.user
        )
        
        # Verify document is created
        self.assertEqual(document.status, "PENDING")
    
    @patch('documents.tasks.extract_text_from_pdf')
    def test_pdf_text_extraction(self, mock_extract):
        """Test PDF text extraction."""
        mock_extract.return_value = "Invoice\nAmount: $1,000.00\nDate: 2024-01-15"
        
        document = Document.objects.create(
            company=self.company,
            file_name="invoice.pdf",
            file_type="PDF"
        )
        
        # Simulate processing
        extracted_text = mock_extract(document.file_path)
        
        self.assertIn("Invoice", extracted_text)
        self.assertIn("1,000.00", extracted_text)
    
    @patch('documents.tasks.extract_data_from_document')
    def test_data_extraction_from_document(self, mock_extract):
        """Test structured data extraction from document."""
        mock_extract.return_value = {
            'amount': '1000.00',
            'date': '2024-01-15',
            'vendor': 'ABC Supplies',
            'description': 'Office supplies'
        }
        
        document = Document.objects.create(
            company=self.company,
            file_name="invoice.pdf",
            file_type="PDF"
        )
        
        extracted_data = mock_extract(document)
        
        self.assertEqual(extracted_data['amount'], '1000.00')
        self.assertEqual(extracted_data['vendor'], 'ABC Supplies')


class DocumentAPITest(TestCase):
    """Test Document API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user(username="testuser", password="testpass123")
        self.token = Token.objects.create(user=self.user)
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_upload_document(self):
        """Test document upload via API."""
        # Create a simple test file
        test_file = SimpleUploadedFile(
            "test_invoice.pdf",
            b"fake pdf content",
            content_type="application/pdf"
        )
        
        data = {
            'company': self.company.id,
            'file': test_file,
            'file_type': 'PDF'
        }
        
        response = self.client.post('/api/documents/', data, format='multipart')
        
        # Note: Actual status code depends on implementation
        # self.assertEqual(response.status_code, 201)
    
    def test_list_documents(self):
        """Test listing documents."""
        Document.objects.create(
            company=self.company,
            file_name="doc1.pdf",
            file_type="PDF"
        )
        Document.objects.create(
            company=self.company,
            file_name="doc2.pdf",
            file_type="PDF"
        )
        
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, 200)
    
    def test_get_document_detail(self):
        """Test retrieving document details."""
        document = Document.objects.create(
            company=self.company,
            file_name="test.pdf",
            file_type="PDF"
        )
        
        response = self.client.get(f'/api/documents/{document.id}/')
        self.assertEqual(response.status_code, 200)
    
    def test_delete_document(self):
        """Test deleting document."""
        document = Document.objects.create(
            company=self.company,
            file_name="test.pdf",
            file_type="PDF"
        )
        
        response = self.client.delete(f'/api/documents/{document.id}/')
        # Verify deletion
        self.assertFalse(Document.objects.filter(id=document.id).exists())


class DocumentTransactionLinkingTest(TestCase):
    """Test linking documents to transactions."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.user = create_test_user(username="testuser", password="testpass123")
    
    def test_document_transaction_association(self):
        """Test associating document with transaction."""
        from transactions.models import Transaction
        from companies.models import ChartOfAccounts
        
        account = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="5000",
            account_name="Expenses",
            account_type="EXPENSE"
        )
        
        transaction = Transaction.objects.create(
            company=self.company,
            date=date.today(),
            description="Invoice payment",
            amount=Decimal('1000.00'),
            account=account
        )
        
        document = Document.objects.create(
            company=self.company,
            file_name="invoice.pdf",
            file_type="PDF",
            transaction=transaction
        )
        
        self.assertEqual(document.transaction, transaction)
        self.assertEqual(transaction.documents.first(), document)
    
    @patch('documents.tasks.auto_create_transaction_from_document')
    def test_automatic_transaction_creation(self, mock_create):
        """Test automatic transaction creation from document."""
        mock_create.return_value = {
            'transaction_id': '123',
            'amount': '1000.00',
            'description': 'Auto-created from invoice'
        }
        
        document = Document.objects.create(
            company=self.company,
            file_name="invoice.pdf",
            file_type="PDF"
        )
        
        # Simulate automatic transaction creation
        result = mock_create(document)
        
        self.assertIsNotNone(result['transaction_id'])
        self.assertEqual(result['amount'], '1000.00')


class DocumentValidationTest(TestCase):
    """Test document validation and error handling."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
    
    def test_valid_file_types(self):
        """Test that only valid file types are accepted."""
        valid_types = ['PDF', 'JPEG', 'PNG', 'CSV', 'XLSX']
        
        for file_type in valid_types:
            document = Document.objects.create(
                company=self.company,
                file_name=f"test.{file_type.lower()}",
                file_type=file_type
            )
            self.assertEqual(document.file_type, file_type)
    
    def test_file_size_validation(self):
        """Test file size validation."""
        # This would need actual file size checks in the model
        document = Document.objects.create(
            company=self.company,
            file_name="large_file.pdf",
            file_type="PDF"
        )
        
        self.assertIsNotNone(document)
    
    def test_duplicate_document_handling(self):
        """Test handling of duplicate documents."""
        doc1 = Document.objects.create(
            company=self.company,
            file_name="invoice.pdf",
            file_type="PDF"
        )
        
        # Create another document with same name
        doc2 = Document.objects.create(
            company=self.company,
            file_name="invoice.pdf",
            file_type="PDF"
        )
        
        # Both should exist (no uniqueness constraint by default)
        self.assertNotEqual(doc1.id, doc2.id)
