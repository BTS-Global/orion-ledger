# MCP Quick Start - Código Base

Este documento contém código pronto para iniciar a implementação do MCP no Orion Ledger.

## 1. Setup Inicial

### Instalar Dependências

```bash
cd backend
pip install mcp>=0.9.0 fastapi uvicorn pydantic anthropic
```

### Estrutura de Diretórios

```bash
mkdir -p mcp_server/{resources,tools,prompts}
touch mcp_server/__init__.py
touch mcp_server/{server,resources,tools,prompts,config,middleware}.py
```

## 2. Server Base (server.py)

```python
"""
MCP Server for Orion Ledger
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mcp import MCPServer, Resource, Tool, Prompt
from typing import Optional
import os

from .middleware import auth_middleware, rate_limit_middleware
from .resources import register_resources
from .tools import register_tools
from .prompts import register_prompts
from .config import settings

# Initialize FastAPI
app = FastAPI(
    title="Orion Ledger MCP Server",
    description="Model Context Protocol Server for AI-powered accounting",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP
mcp = MCPServer(
    name="orion-ledger",
    version="1.0.0",
    description="Accounting and financial data access via MCP"
)

# Register components
register_resources(mcp)
register_tools(mcp)
register_prompts(mcp)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "mcp_version": mcp.version
    }

# MCP endpoints
@app.get("/mcp/info")
async def mcp_info():
    """Get MCP server information."""
    return {
        "name": mcp.name,
        "version": mcp.version,
        "description": mcp.description,
        "resources": len(mcp.resources),
        "tools": len(mcp.tools),
        "prompts": len(mcp.prompts)
    }

# Mount MCP to FastAPI
app.mount("/mcp", mcp.app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
```

## 3. Configuration (config.py)

```python
"""
MCP Server Configuration
"""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8001
    
    # Security
    API_KEY_HEADER: str = "X-Orion-API-Key"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # LLM Providers
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Models
    DEFAULT_MODEL: str = "claude-3-sonnet"
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    
    # Database
    DATABASE_URL: str = "postgresql://..."
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 4. Middleware (middleware.py)

```python
"""
Authentication and rate limiting middleware
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import redis
import hashlib

from .config import settings

# Redis client for rate limiting
redis_client = redis.from_url(settings.REDIS_URL)

async def auth_middleware(request: Request, call_next):
    """Validate API key."""
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    api_key = request.headers.get(settings.API_KEY_HEADER)
    if not api_key:
        return JSONResponse(
            status_code=401,
            content={"error": "Missing API key"}
        )
    
    # Validate API key (replace with actual validation)
    if not validate_api_key(api_key):
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid API key"}
        )
    
    # Add company_id to request state
    request.state.company_id = get_company_from_api_key(api_key)
    request.state.api_key = api_key
    
    return await call_next(request)

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting per company."""
    if request.url.path in ["/health"]:
        return await call_next(request)
    
    api_key = request.headers.get(settings.API_KEY_HEADER, "")
    key_hash = hashlib.md5(api_key.encode()).hexdigest()
    
    # Check rate limit
    minute_key = f"rate_limit:minute:{key_hash}"
    minute_count = redis_client.incr(minute_key)
    if minute_count == 1:
        redis_client.expire(minute_key, 60)
    
    if minute_count > settings.RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "limit": settings.RATE_LIMIT_PER_MINUTE,
                "window": "1 minute"
            }
        )
    
    return await call_next(request)

def validate_api_key(api_key: str) -> bool:
    """Validate API key against database."""
    # TODO: Implement actual validation
    return len(api_key) > 10

def get_company_from_api_key(api_key: str) -> str:
    """Extract company ID from API key."""
    # TODO: Implement actual lookup
    return "company_uuid"
```

## 5. Resources (resources.py)

```python
"""
MCP Resources - Data access
"""
from mcp import Resource
from typing import Dict, Any
import json

def register_resources(mcp_server):
    """Register all MCP resources."""
    
    @mcp_server.resource("companies/{company_id}")
    async def get_company(company_id: str, context: Dict[str, Any]) -> Dict:
        """Get company information."""
        from companies.models import Company
        
        try:
            company = Company.objects.select_related().get(id=company_id)
            
            return {
                "uri": f"companies/{company_id}",
                "mimeType": "application/json",
                "text": json.dumps({
                    "id": str(company.id),
                    "name": company.name,
                    "tax_id": company.tax_id,
                    "jurisdiction": company.jurisdiction,
                    "entity_type": company.entity_type,
                    "fiscal_year_start": company.fiscal_year_start.isoformat(),
                    "industry": company.industry or "N/A",
                    "size": company.size or "N/A",
                })
            }
        except Company.DoesNotExist:
            return {
                "uri": f"companies/{company_id}",
                "error": "Company not found"
            }
    
    @mcp_server.resource("companies/{company_id}/chart-of-accounts")
    async def get_chart_of_accounts(company_id: str, context: Dict[str, Any]) -> Dict:
        """Get chart of accounts."""
        from companies.models import ChartOfAccounts
        from django.db.models import Count
        
        accounts = ChartOfAccounts.objects.filter(
            company_id=company_id,
            is_active=True
        ).order_by('account_code')
        
        # Group by type
        accounts_by_type = {}
        for account in accounts:
            account_type = account.account_type
            if account_type not in accounts_by_type:
                accounts_by_type[account_type] = []
            
            accounts_by_type[account_type].append({
                "code": account.account_code,
                "name": account.account_name,
                "type": account.account_type,
                "balance": float(account.current_balance or 0)
            })
        
        return {
            "uri": f"companies/{company_id}/chart-of-accounts",
            "mimeType": "application/json",
            "text": json.dumps({
                "total_accounts": accounts.count(),
                "accounts_by_type": accounts_by_type,
                "summary": {
                    "ASSET": len(accounts_by_type.get("ASSET", [])),
                    "LIABILITY": len(accounts_by_type.get("LIABILITY", [])),
                    "EQUITY": len(accounts_by_type.get("EQUITY", [])),
                    "REVENUE": len(accounts_by_type.get("REVENUE", [])),
                    "EXPENSE": len(accounts_by_type.get("EXPENSE", []))
                }
            })
        }
    
    @mcp_server.resource("companies/{company_id}/transactions/recent")
    async def get_recent_transactions(company_id: str, context: Dict[str, Any]) -> Dict:
        """Get recent transactions."""
        from transactions.models import Transaction
        from datetime import date, timedelta
        
        # Last 30 days
        start_date = date.today() - timedelta(days=30)
        
        transactions = Transaction.objects.filter(
            company_id=company_id,
            date__gte=start_date
        ).select_related('account').order_by('-date')[:100]
        
        trans_list = []
        for trans in transactions:
            trans_list.append({
                "id": str(trans.id),
                "date": trans.date.isoformat(),
                "description": trans.description,
                "amount": float(trans.amount),
                "account": {
                    "code": trans.account.account_code if trans.account else None,
                    "name": trans.account.account_name if trans.account else None
                },
                "status": trans.status,
                "is_validated": trans.is_validated
            })
        
        return {
            "uri": f"companies/{company_id}/transactions/recent",
            "mimeType": "application/json",
            "text": json.dumps({
                "count": len(trans_list),
                "period": {
                    "start": start_date.isoformat(),
                    "end": date.today().isoformat()
                },
                "transactions": trans_list
            })
        }
```

## 6. Tools (tools.py)

```python
"""
MCP Tools - Executable actions
"""
from mcp import Tool
from typing import Dict, Any
from pydantic import BaseModel, Field

def register_tools(mcp_server):
    """Register all MCP tools."""
    
    class ClassifyTransactionInput(BaseModel):
        company_id: str = Field(..., description="Company UUID")
        description: str = Field(..., description="Transaction description")
        amount: float = Field(..., description="Transaction amount")
        date: str = Field(..., description="Transaction date (ISO format)")
        vendor: str = Field(None, description="Vendor/supplier name")
    
    @mcp_server.tool("classify_transaction")
    async def classify_transaction(params: ClassifyTransactionInput) -> Dict[str, Any]:
        """
        Classify a transaction using AI with historical context.
        Returns suggested account with confidence score.
        """
        from core.rag_service import rag_service
        
        # Generate embedding
        transaction_data = {
            "description": params.description,
            "amount": params.amount,
            "vendor": params.vendor or "",
            "date": params.date
        }
        
        embedding = rag_service.generate_transaction_embedding(transaction_data)
        
        if not embedding:
            return {
                "error": "Failed to generate embedding",
                "suggested_account": None
            }
        
        # Find similar transactions
        similar = rag_service.find_similar_transactions(
            embedding,
            params.company_id,
            top_k=5
        )
        
        # Get most common account from similar transactions
        if similar:
            # Simple majority vote
            account_votes = {}
            for s in similar:
                acc = s.get('account_code')
                if acc:
                    account_votes[acc] = account_votes.get(acc, 0) + s.get('similarity', 0)
            
            best_account = max(account_votes.items(), key=lambda x: x[1])
            
            # Find account details
            from companies.models import ChartOfAccounts
            try:
                account = ChartOfAccounts.objects.get(
                    company_id=params.company_id,
                    account_code=best_account[0]
                )
                
                return {
                    "suggested_account": {
                        "code": account.account_code,
                        "name": account.account_name,
                        "confidence": min(best_account[1], 1.0)
                    },
                    "similar_transactions": similar[:3],
                    "reasoning": f"Based on {len(similar)} similar historical transactions"
                }
            except ChartOfAccounts.DoesNotExist:
                pass
        
        return {
            "suggested_account": None,
            "similar_transactions": [],
            "reasoning": "No similar historical transactions found"
        }
    
    class CreateJournalEntryInput(BaseModel):
        company_id: str
        date: str
        description: str
        lines: list
    
    @mcp_server.tool("create_journal_entry")
    async def create_journal_entry(params: CreateJournalEntryInput) -> Dict[str, Any]:
        """
        Create a journal entry with double-entry validation.
        """
        from transactions.models import JournalEntry, JournalEntryLine
        from companies.models import ChartOfAccounts
        from decimal import Decimal
        from datetime import datetime
        
        # Validate balanced entry
        total_debit = sum(Decimal(str(line.get('debit', 0))) for line in params.lines)
        total_credit = sum(Decimal(str(line.get('credit', 0))) for line in params.lines)
        
        if total_debit != total_credit:
            return {
                "success": False,
                "error": "Unbalanced entry",
                "total_debit": float(total_debit),
                "total_credit": float(total_credit),
                "difference": float(total_debit - total_credit)
            }
        
        # Create entry
        try:
            entry = JournalEntry.objects.create(
                company_id=params.company_id,
                date=datetime.fromisoformat(params.date).date(),
                description=params.description,
                created_by=None  # TODO: Get from context
            )
            
            # Create lines
            for line in params.lines:
                account = ChartOfAccounts.objects.get(
                    company_id=params.company_id,
                    account_code=line['account_code']
                )
                
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=account,
                    debit=Decimal(str(line.get('debit', 0))),
                    credit=Decimal(str(line.get('credit', 0))),
                    description=line.get('description', '')
                )
            
            return {
                "success": True,
                "journal_entry_id": str(entry.id),
                "total_lines": len(params.lines),
                "total_amount": float(total_debit)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

## 7. Prompts (prompts.py)

```python
"""
MCP Prompts - Reusable templates
"""
from mcp import Prompt
from typing import Dict, Any

def register_prompts(mcp_server):
    """Register all MCP prompts."""
    
    @mcp_server.prompt("accounting_assistant")
    async def accounting_assistant_prompt(context: Dict[str, Any]) -> str:
        """General accounting assistant prompt."""
        company_name = context.get('company_name', 'Unknown Company')
        
        return f"""You are a professional accounting assistant for {company_name}.

Your responsibilities:
- Help classify transactions accurately
- Explain accounting principles clearly
- Generate financial reports
- Identify anomalies and potential errors
- Ensure compliance with accounting standards

Guidelines:
- Always follow double-entry bookkeeping
- Be precise with numbers and dates
- Ask for clarification when needed
- Explain your reasoning
- Use professional but accessible language

Available data:
- Chart of accounts
- Historical transactions
- Financial reports
- Account balances

How can I assist you today?"""
    
    @mcp_server.prompt("classify_batch")
    async def classify_batch_prompt(context: Dict[str, Any]) -> str:
        """Batch classification prompt."""
        transactions = context.get('transactions', [])
        
        prompt = """Classify the following transactions consistently:

"""
        for i, trans in enumerate(transactions, 1):
            prompt += f"""
Transaction {i}:
- Description: {trans.get('description')}
- Amount: ${trans.get('amount', 0):,.2f}
- Date: {trans.get('date')}
- Vendor: {trans.get('vendor', 'N/A')}

"""
        
        prompt += """
Return a JSON array with classifications:
[
  {
    "transaction_index": 1,
    "suggested_account": "XXXX",
    "confidence": 0.XX,
    "reasoning": "..."
  },
  ...
]

Ensure consistency across similar transactions."""
        
        return prompt
```

## 8. Run Script (run_mcp.sh)

```bash
#!/bin/bash

# Orion Ledger MCP Server Startup Script

echo "🚀 Starting Orion Ledger MCP Server..."

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo "📦 Checking dependencies..."
pip install -q -r requirements-mcp.txt

# Set environment
export DJANGO_SETTINGS_MODULE=backend.settings
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run migrations if needed
echo "🔄 Checking database..."
python manage.py migrate --no-input

# Start MCP server
echo "✨ Starting MCP server on port 8001..."
cd mcp_server
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

echo "✅ MCP Server running at http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo "🔍 MCP Info: http://localhost:8001/mcp/info"
```

## 9. Claude Desktop Config

```json
{
  "mcpServers": {
    "orion-ledger": {
      "command": "python",
      "args": [
        "/path/to/orion-ledger/backend/mcp_server/server.py"
      ],
      "env": {
        "ORION_API_KEY": "your-api-key-here",
        "DJANGO_SETTINGS_MODULE": "backend.settings",
        "PYTHONPATH": "/path/to/orion-ledger/backend"
      }
    }
  }
}
```

## 10. Testing Script (test_mcp.py)

```python
"""
Test MCP Server
"""
import asyncio
import httpx

async def test_mcp_server():
    """Test MCP server endpoints."""
    base_url = "http://localhost:8001"
    headers = {"X-Orion-API-Key": "test-key-123"}
    
    async with httpx.AsyncClient() as client:
        # Health check
        print("🏥 Testing health check...")
        response = await client.get(f"{base_url}/health")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        
        # MCP info
        print("\nℹ️ Testing MCP info...")
        response = await client.get(
            f"{base_url}/mcp/info",
            headers=headers
        )
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        
        # Get company resource
        print("\n🏢 Testing company resource...")
        company_id = "your-company-uuid"
        response = await client.get(
            f"{base_url}/mcp/resources/companies/{company_id}",
            headers=headers
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Company: {response.json()}")
        
        # Classify transaction tool
        print("\n🔍 Testing classification tool...")
        response = await client.post(
            f"{base_url}/mcp/tools/classify_transaction",
            headers=headers,
            json={
                "company_id": company_id,
                "description": "Office supplies from Staples",
                "amount": 150.00,
                "date": "2024-11-16",
                "vendor": "Staples Inc"
            }
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  Suggested account: {result.get('suggested_account')}")
            print(f"  Confidence: {result.get('suggested_account', {}).get('confidence')}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```

## 11. Next Steps

1. **Setup básico**:
   ```bash
   chmod +x run_mcp.sh
   ./run_mcp.sh
   ```

2. **Testar servidor**:
   ```bash
   python test_mcp.py
   ```

3. **Integrar com Claude Desktop**:
   - Copiar config para `~/.config/claude/config.json`
   - Reiniciar Claude Desktop
   - Testar: "Mostre as informações da empresa X"

4. **Próximas implementações**:
   - Adicionar mais resources
   - Implementar tools avançados
   - Criar prompts personalizados
   - Setup de monitoring

---

**Pronto para começar!** 🚀

Este código base fornece todos os componentes essenciais para ter um MCP Server funcional integrado ao Orion Ledger.
