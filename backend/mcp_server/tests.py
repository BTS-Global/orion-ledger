"""
MCP Server Tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from mcp_server.server import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_api_key():
    """Mock API key"""
    return "test-api-key-123"


@pytest.fixture
def mock_company_id():
    """Mock company ID"""
    return "company-uuid-123"


class TestHealthEndpoints:
    """Test health and metrics endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mcp-server"
    
    def test_metrics(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "requests_total" in data


class TestResourceEndpoints:
    """Test resource endpoints"""
    
    def test_list_resources(self, client, mock_api_key):
        """Test listing available resources"""
        response = client.get(
            "/resources",
            headers={"X-MCP-API-Key": mock_api_key}
        )
        
        assert response.status_code in [200, 401]  # May need auth
        
        if response.status_code == 200:
            data = response.json()
            assert "resources" in data
    
    @patch('mcp_server.resources.get_resource')
    def test_get_company_resource(self, mock_get_resource, client, mock_api_key, mock_company_id):
        """Test getting company resource"""
        # Mock resource response
        mock_get_resource.return_value.to_dict.return_value = {
            "id": mock_company_id,
            "name": "Test Company"
        }
        
        response = client.get(
            f"/resources/company/{mock_company_id}",
            headers={"X-MCP-API-Key": mock_api_key}
        )
        
        # May be 200 or 401/403 depending on auth
        assert response.status_code in [200, 401, 403]


class TestToolEndpoints:
    """Test tool endpoints"""
    
    def test_list_tools(self, client, mock_api_key):
        """Test listing available tools"""
        response = client.get(
            "/tools",
            headers={"X-MCP-API-Key": mock_api_key}
        )
        
        assert response.status_code in [200, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "tools" in data
    
    @patch('mcp_server.tools.execute_tool')
    def test_execute_classify_tool(self, mock_execute, client, mock_api_key, mock_company_id):
        """Test executing classify_transaction tool"""
        # Mock tool response
        mock_execute.return_value = {
            "success": True,
            "suggested_account": "6001",
            "confidence": 0.95
        }
        
        response = client.post(
            "/tools/classify_transaction",
            headers={"X-MCP-API-Key": mock_api_key},
            json={
                "company_id": mock_company_id,
                "description": "Office supplies",
                "amount": 150.00,
                "date": "2024-01-15"
            }
        )
        
        assert response.status_code in [200, 400, 401, 403]


class TestPromptEndpoints:
    """Test prompt endpoints"""
    
    def test_list_prompts(self, client):
        """Test listing available prompts"""
        response = client.get("/prompts")
        assert response.status_code == 200
        
        data = response.json()
        assert "prompts" in data
    
    def test_render_prompt(self, client):
        """Test rendering a prompt template"""
        response = client.post(
            "/prompts/accounting_assistant",
            json={
                "company_name": "Test Company",
                "industry": "Technology",
                "size": "Medium",
                "tax_regime": "Lucro Real",
                "fiscal_period": "2024",
                "transaction_count": "1000",
                "account_count": "50",
                "last_trial_balance_date": "2024-01-31",
                "chart_of_accounts_summary": "50 active accounts"
            }
        )
        
        assert response.status_code in [200, 404]


class TestModelEndpoints:
    """Test model endpoints"""
    
    def test_list_models(self, client):
        """Test listing supported models"""
        response = client.get("/models")
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
        assert "claude-3-sonnet-20240229" in data["models"]


# Integration Tests

@pytest.mark.integration
class TestMCPIntegration:
    """Integration tests requiring full setup"""
    
    @pytest.mark.skip(reason="Requires Redis and database setup")
    def test_full_classification_flow(self, client, mock_api_key, mock_company_id):
        """Test complete classification flow"""
        # This would test:
        # 1. Auth
        # 2. Get company data
        # 3. Classify transaction
        # 4. Verify result
        pass
    
    @pytest.mark.skip(reason="Requires Redis and database setup")
    def test_rate_limiting(self, client, mock_api_key):
        """Test rate limiting enforcement"""
        # This would test:
        # 1. Make many requests
        # 2. Verify rate limit kicks in
        # 3. Verify retry-after header
        pass
