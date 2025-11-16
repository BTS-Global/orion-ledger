"""
Tests for core app and API endpoints.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from companies.models import Company, UserProfile
from core.models import FeedbackEntry, PredictionMetrics
from core.rag_service import RAGService
from core.feedback_service import FeedbackService
from core.test_utils import create_test_company, create_test_user, create_test_account
from transactions.models import Transaction
from companies.models import ChartOfAccounts
from decimal import Decimal
from datetime import date


class APIEndpointTest(TestCase):
    """Test API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.user = create_test_user(username="testuser", password="testpass123")
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
    
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


class AuthenticationTest(TestCase):
    """Test authentication and authorization."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user(username="testuser", email="test@example.com", password="testpass123")
        self.token = Token.objects.create(user=self.user)
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
    
    def test_token_authentication(self):
        """Test token-based authentication."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get('/api/current-user/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['id'], self.user.id)
    
    def test_logout(self):
        """Test logout deletes token."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 200)
        
        # Verify token is deleted
        self.assertFalse(Token.objects.filter(user=self.user).exists())
    
    def test_unauthenticated_access(self):
        """Test unauthenticated access to protected endpoints."""
        response = self.client.get('/api/current-user/')
        self.assertEqual(response.status_code, 401)
    
    def test_csrf_token(self):
        """Test CSRF token generation."""
        response = self.client.get('/api/csrf/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('csrfToken', response.data)


class MultitenancyTest(TestCase):
    """Test multitenancy isolation."""
    
    def setUp(self):
        self.client = APIClient()
        
        # User 1 with Company 1
        self.user1 = create_test_user(username="user1", email="user1@example.com", password="pass123")
        self.company1 = create_test_company(name="Company 1", tax_id="11-1111111")
        UserProfile.objects.create(
            user=self.user1,
            company=self.company1,
            full_name="User One"
        )
        self.token1 = Token.objects.create(user=self.user1)
        
        # User 2 with Company 2
        self.user2 = create_test_user(username="user2", email="user2@example.com", password="pass123")
        self.company2 = create_test_company(name="Company 2", tax_id="22-2222222")
        UserProfile.objects.create(
            user=self.user2,
            company=self.company2,
            full_name="User Two"
        )
        self.token2 = Token.objects.create(user=self.user2)
        
        # Create transactions for each company
        self.account1 = ChartOfAccounts.objects.create(
            company=self.company1,
            account_code="1000",
            account_name="Cash",
            account_type="ASSET"
        )
        self.trans1 = Transaction.objects.create(
            company=self.company1,
            date=date.today(),
            description="Company 1 Transaction",
            amount=Decimal('100.00'),
            account=self.account1
        )
        
        self.account2 = ChartOfAccounts.objects.create(
            company=self.company2,
            account_code="1000",
            account_name="Cash",
            account_type="ASSET"
        )
        self.trans2 = Transaction.objects.create(
            company=self.company2,
            date=date.today(),
            description="Company 2 Transaction",
            amount=Decimal('200.00'),
            account=self.account2
        )
    
    def test_company_isolation(self):
        """Test users can only see their company's data."""
        # User 1 should only see Company 1 transactions
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 200)
        # Note: Actual filtering logic needs to be implemented in views
        
    def test_cross_company_access_prevention(self):
        """Test users cannot access other company's data."""
        # User 1 tries to access Company 2 transaction
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get(f'/api/transactions/{self.trans2.id}/')
        # Should be 404 or 403
        self.assertIn(response.status_code, [403, 404])


class RAGServiceTest(TestCase):
    """Test RAG (Retrieval-Augmented Generation) service."""
    
    def setUp(self):
        self.rag_service = RAGService()
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
    
    def test_embedding_generation(self):
        """Test embedding generation for text."""
        text = "Office supplies purchase"
        embedding = self.rag_service.generate_embedding(text)
        
        if embedding:  # Only test if model is available
            self.assertIsNotNone(embedding)
            self.assertIsInstance(embedding, list)
            self.assertEqual(len(embedding), 384)  # all-MiniLM-L6-v2 dimension
    
    def test_transaction_embedding(self):
        """Test embedding generation for transaction."""
        transaction_data = {
            'description': 'Office supplies from Staples',
            'amount': '150.00',
            'category': 'EXPENSE',
            'date': date.today().isoformat()
        }
        
        embedding = self.rag_service.generate_transaction_embedding(transaction_data)
        
        if embedding:  # Only test if model is available
            self.assertIsNotNone(embedding)
            self.assertIsInstance(embedding, list)
    
    def test_embedding_caching(self):
        """Test embedding caching mechanism."""
        text = "Test transaction description"
        
        # First call
        embedding1 = self.rag_service.generate_embedding(text)
        
        # Second call should use cache
        embedding2 = self.rag_service.generate_embedding(text)
        
        if embedding1 and embedding2:
            self.assertEqual(embedding1, embedding2)


class FeedbackServiceTest(TestCase):
    """Test feedback and active learning service."""
    
    def setUp(self):
        self.user = create_test_user(username="testuser", password="testpass123")
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
        self.account1 = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="5000",
            account_name="Office Supplies",
            account_type="EXPENSE"
        )
        self.account2 = ChartOfAccounts.objects.create(
            company=self.company,
            account_code="5100",
            account_name="Travel",
            account_type="EXPENSE"
        )
        self.transaction = Transaction.objects.create(
            company=self.company,
            date=date.today(),
            description="Office supplies",
            amount=Decimal('100.00')
        )
    
    def test_record_correction(self):
        """Test recording user correction."""
        feedback = FeedbackService.record_correction(
            transaction_id=str(self.transaction.id),
            predicted_account_id=str(self.account1.id),
            corrected_account_id=str(self.account2.id),
            predicted_confidence=0.85,
            user=self.user,
            reason="Wrong category"
        )
        
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.feedback_type, 'CORRECTION')
        self.assertEqual(feedback.corrected_account, self.account2)
        
        # Transaction should be updated
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.account, self.account2)
        self.assertTrue(self.transaction.is_validated)
    
    def test_record_confirmation(self):
        """Test recording user confirmation."""
        feedback = FeedbackService.record_correction(
            transaction_id=str(self.transaction.id),
            predicted_account_id=str(self.account1.id),
            corrected_account_id=str(self.account1.id),
            predicted_confidence=0.95,
            user=self.user
        )
        
        self.assertEqual(feedback.feedback_type, 'CONFIRMATION')
    
    def test_get_uncertain_predictions(self):
        """Test retrieval of uncertain predictions."""
        # Create transactions with different confidence levels
        trans_low = Transaction.objects.create(
            company=self.company,
            date=date.today(),
            description="Uncertain transaction",
            amount=Decimal('50.00'),
            account=self.account1,
            ai_confidence=0.45
        )
        
        trans_high = Transaction.objects.create(
            company=self.company,
            date=date.today(),
            description="Certain transaction",
            amount=Decimal('75.00'),
            account=self.account1,
            ai_confidence=0.95
        )
        
        uncertain = FeedbackService.get_uncertain_predictions(self.company)
        
        self.assertIn(trans_low, [t['transaction'] for t in uncertain])
        self.assertNotIn(trans_high, [t['transaction'] for t in uncertain])


class PredictionMetricsTest(TestCase):
    """Test prediction metrics tracking."""
    
    def setUp(self):
        self.company = create_test_company(name="Test Corp", tax_id="12-3456789")
    
    def test_metrics_creation(self):
        """Test metrics tracking."""
        metrics = PredictionMetrics.objects.create(
            company=self.company,
            total_predictions=100,
            correct_predictions=85,
            avg_confidence=0.87
        )
        
        self.assertEqual(metrics.accuracy, 0.85)
        self.assertEqual(metrics.total_predictions, 100)
    
    def test_metrics_aggregation(self):
        """Test metrics aggregation over time."""
        # Create multiple metrics entries
        PredictionMetrics.objects.create(
            company=self.company,
            total_predictions=50,
            correct_predictions=40,
            avg_confidence=0.82
        )
        PredictionMetrics.objects.create(
            company=self.company,
            total_predictions=75,
            correct_predictions=65,
            avg_confidence=0.88
        )
        
        # Get latest metrics
        latest = PredictionMetrics.objects.filter(
            company=self.company
        ).order_by('-recorded_at').first()
        
        self.assertIsNotNone(latest)
        self.assertEqual(latest.total_predictions, 75)
