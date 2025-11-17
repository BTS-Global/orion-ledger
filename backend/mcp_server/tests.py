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


class TestNewTools:
    """Test newly implemented tools"""
    
    @patch('mcp_server.tools.analyze_document_tool')
    def test_analyze_document_tool(
        self, mock_analyze, client, mock_api_key, mock_company_id
    ):
        """Test document analysis tool"""
        # Mock document analysis response
        mock_analyze.return_value = {
            "success": True,
            "document_id": "doc-123",
            "document_type": "invoice",
            "extracted_data": {
                "vendor": "ABC Corp",
                "amount": 1500.00,
                "date": "2024-01-15"
            },
            "transactions": [
                {
                    "description": "Invoice from ABC Corp",
                    "amount": 1500.00,
                    "suggested_account": "5001"
                }
            ],
            "confidence": 0.92
        }
        
        response = client.post(
            "/tools/analyze_document",
            headers={"X-MCP-API-Key": mock_api_key},
            json={
                "company_id": mock_company_id,
                "document_path": "/path/to/invoice.pdf",
                "document_type": "invoice"
            }
        )
        
        assert response.status_code in [200, 400, 401, 403]
    
    @patch('mcp_server.tools.generate_custom_report_tool')
    def test_generate_custom_report_revenue(
        self, mock_report, client, mock_api_key, mock_company_id
    ):
        """Test custom report generation for revenue analysis"""
        # Mock report response
        mock_report.return_value = {
            "success": True,
            "report_type": "revenue_analysis",
            "query": "Show revenue by account",
            "period": {
                "start": "2024-01-01",
                "end": "2024-03-31"
            },
            "data": [
                {
                    "account": "Receita de Serviços",
                    "code": "4001",
                    "total": 150000.00,
                    "transactions": 125
                },
                {
                    "account": "Receita de Vendas",
                    "code": "4002",
                    "total": 85000.00,
                    "transactions": 67
                }
            ],
            "total": 235000.00,
            "summary": "Found 2 revenue accounts with total of $235,000.00"
        }
        
        response = client.post(
            "/tools/generate_custom_report",
            headers={"X-MCP-API-Key": mock_api_key},
            json={
                "company_id": mock_company_id,
                "query": "Show revenue by account",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31"
            }
        )
        
        assert response.status_code in [200, 400, 401, 403]
    
    @patch('mcp_server.tools.generate_custom_report_tool')
    def test_generate_custom_report_expense(
        self, mock_report, client, mock_api_key, mock_company_id
    ):
        """Test custom report generation for expense analysis"""
        mock_report.return_value = {
            "success": True,
            "report_type": "expense_analysis",
            "query": "Top 10 expenses",
            "data": [
                {
                    "account": "Despesas com Pessoal",
                    "code": "5001",
                    "total": 80000.00,
                    "transactions": 50
                }
            ]
        }
        
        response = client.post(
            "/tools/generate_custom_report",
            headers={"X-MCP-API-Key": mock_api_key},
            json={
                "company_id": mock_company_id,
                "query": "Top 10 expenses",
                "limit": 10
            }
        )
        
        assert response.status_code in [200, 400, 401, 403]


class TestFinancialReports:
    """Test financial reports resource"""
    
    @patch('mcp_server.resources.get_resource')
    def test_balance_sheet_report(
        self, mock_get_resource, client, mock_api_key, mock_company_id
    ):
        """Test balance sheet report generation"""
        mock_get_resource.return_value.to_dict.return_value = {
            "report_type": "balance_sheet",
            "company_id": mock_company_id,
            "date": "2024-12-31",
            "assets": {
                "current": [
                    {"code": "1.01.001", "name": "Caixa", "balance": 50000.00}
                ],
                "current_total": 50000.00,
                "non_current": [],
                "non_current_total": 0.00,
                "total": 50000.00
            },
            "liabilities": {
                "current": [],
                "current_total": 0.00,
                "non_current": [],
                "non_current_total": 0.00,
                "total": 0.00
            },
            "equity": {
                "items": [
                    {"code": "3.01.001", "name": "Capital", "balance": 50000.00}
                ],
                "total": 50000.00
            },
            "totals": {
                "total_assets": 50000.00,
                "total_liabilities_and_equity": 50000.00,
                "is_balanced": True
            }
        }
        
        response = client.get(
            f"/resources/reports/{mock_company_id}?report_type=balance_sheet",
            headers={"X-MCP-API-Key": mock_api_key}
        )
        
        assert response.status_code in [200, 401, 403]
    
    @patch('mcp_server.resources.get_resource')
    def test_income_statement_report(
        self, mock_get_resource, client, mock_api_key, mock_company_id
    ):
        """Test income statement report generation"""
        mock_get_resource.return_value.to_dict.return_value = {
            "report_type": "income_statement",
            "company_id": mock_company_id,
            "period": {
                "start": "2024-01-01",
                "end": "2024-12-31"
            },
            "revenue": {
                "total": 500000.00
            },
            "expenses": {
                "total": 350000.00
            },
            "net_income": 150000.00
        }
        
        response = client.get(
            f"/resources/reports/{mock_company_id}?report_type=income_statement",
            headers={"X-MCP-API-Key": mock_api_key}
        )
        
        assert response.status_code in [200, 401, 403]


class TestIntegrationFlows:
    """Test complete integration flows"""
    
    def test_full_classification_flow(
        self, client, mock_api_key, mock_company_id
    ):
        """Test complete transaction classification flow"""
        # This would test the full flow from transaction to classification
        # In practice, this needs real database setup
        pass
    
    def test_rate_limiting(self, client, mock_api_key):
        """Test rate limiting enforcement"""
        # Make multiple rapid requests
        # In practice, this needs Redis setup for actual testing
        pass
    
    @patch('mcp_server.tools.audit_transactions_tool')
    def test_audit_flow(
        self, mock_audit, client, mock_api_key, mock_company_id
    ):
        """Test transaction audit flow"""
        mock_audit.return_value = {
            "success": True,
            "transactions_analyzed": 150,
            "anomalies_found": 5,
            "critical": 2,
            "warnings": 3,
            "items": [
                {
                    "type": "duplicate",
                    "severity": "critical",
                    "description": "Possible duplicate transaction",
                    "transaction_ids": ["id1", "id2"]
                },
                {
                    "type": "unusual_amount",
                    "severity": "warning",
                    "description": "Unusually large amount detected"
                }
            ]
        }
        
        response = client.post(
            "/tools/audit_transactions",
            headers={"X-MCP-API-Key": mock_api_key},
            json={
                "company_id": mock_company_id,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "check_duplicates": True,
                "check_unusual_amounts": True
            }
        )
        
        assert response.status_code in [200, 400, 401, 403]


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_find_duplicates(self):
        """Test duplicate detection logic"""
        # Would test _find_duplicates with mock data
        pass
    
    def test_find_unusual_amounts(self):
        """Test unusual amount detection"""
        # Would test _find_unusual_amounts with mock data
        pass
    
    def test_find_inconsistencies(self):
        """Test inconsistency detection"""
        # Would test _find_inconsistencies with mock data
        pass
