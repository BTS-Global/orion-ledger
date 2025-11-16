"""
Tests for core app and API endpoints.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from companies.models import Company


class APIEndpointTest(TestCase):
    """Test API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.company = Company.objects.create(
            company_name="Test Corp",
            tax_id="12-3456789"
        )
    
    def test_companies_endpoint(self):
        """Test companies API endpoint."""
        response = self.client.get('/api/companies/')
        self.assertEqual(response.status_code, 200)
    
    def test_transactions_endpoint(self):
        """Test transactions API endpoint."""
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 200)
    
    def test_documents_endpoint(self):
        """Test documents API endpoint."""
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, 200)
    
    def test_irs_forms_endpoint(self):
        """Test IRS forms API endpoint."""
        response = self.client.get('/api/irs-forms/')
        self.assertEqual(response.status_code, 200)
    
    def test_auth_status_endpoint(self):
        """Test auth status API endpoint."""
        response = self.client.get('/api/auth/status/')
        self.assertEqual(response.status_code, 200)
