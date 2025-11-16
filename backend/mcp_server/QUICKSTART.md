# Orion Ledger - MCP Server

**Model Context Protocol (MCP) Implementation**

## Status

🎉 **Fase 1: COMPLETA** ✅

O MCP Server está 100% implementado e operacional!

## Quick Links

- 🚀 **[Quickstart Guide](../../docs/MCP_QUICKSTART.md)** - Como iniciar em 5 minutos
- 📖 **[README Técnico](README.md)** - Documentação completa da API
- 📋 **[Implementation Plan](../../docs/MCP_IMPLEMENTATION_PLAN.md)** - Plano completo
- ✅ **[Phase 1 Complete](../../docs/MCP_PHASE1_COMPLETE.md)** - Resumo da entrega

## Início Rápido

```bash
# 1. Instalar dependências
cd backend
pip install -r requirements-mcp.txt

# 2. Aplicar migrations
python3 manage.py migrate core

# 3. Criar API key (Django shell)
python3 manage.py shell
>>> from core.models import APIKey
>>> from companies.models import Company
>>> key = APIKey.objects.create(
...     company=Company.objects.first(),
...     name="Dev Key",
...     can_classify=True
... )
>>> print(key.key)
>>> exit()

# 4. Iniciar servidor
./run_mcp_server.sh

# 5. Testar
curl http://localhost:8001/health
```

## Estrutura

```
mcp_server/
├── __init__.py       # Module initialization
├── server.py         # FastAPI server (349 LOC)
├── config.py         # Settings (107 LOC)
├── middleware.py     # Auth, rate limit, audit (235 LOC)
├── resources.py      # 4 MCP resources (234 LOC)
├── tools.py          # 3 MCP tools (370 LOC)
├── prompts.py        # 7 prompt templates (234 LOC)
├── tests.py          # Test suite (182 LOC)
└── README.md         # This file
```

## Funcionalidades

### ✅ Implementado (Fase 1)

- **Autenticação**: APIKey model + middleware
- **Rate Limiting**: 100/min, 1000/hour via Redis
- **Audit Logging**: Todas as operações registradas
- **Resources**: company, chart_of_accounts, transactions, reports
- **Tools**: classify_transaction, create_journal_entry, audit_transactions
- **Prompts**: 7 templates reutilizáveis

### 🔜 Próximas Fases

- **Fase 2**: Recursos avançados (balance sheet, income statement)
- **Fase 3**: Tools avançadas (reconciliação, fraude)
- **Fase 4**: Streaming & multi-LLM
- **Fase 5**: Integração Claude Desktop
- **Fase 6**: Production deployment

## Endpoints

### Resources
- `GET /resources` - Listar resources disponíveis
- `GET /resources/{type}/{company_id}` - Acessar resource específico

### Tools
- `GET /tools` - Listar tools disponíveis
- `POST /tools/{name}` - Executar tool

### Prompts
- `GET /prompts` - Listar prompts
- `POST /prompts/{name}` - Renderizar prompt

### Health
- `GET /health` - Health check
- `GET /metrics` - Métricas do servidor

## Documentação Interativa

Acesse: **http://localhost:8001/docs**

## Exemplos

### Classificar Transação

```bash
curl -X POST \
  -H "X-MCP-API-Key: orion_mcp_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "uuid",
    "description": "Office supplies",
    "amount": 150.00,
    "date": "2024-01-15"
  }' \
  http://localhost:8001/tools/classify_transaction
```

### Auditar Transações

```bash
curl -X POST \
  -H "X-MCP-API-Key: orion_mcp_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "uuid",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "check_duplicates": true
  }' \
  http://localhost:8001/tools/audit_transactions
```

## Suporte

- 📖 Documentação completa: [README.md](README.md)
- 🚀 Guia de início: [MCP_QUICKSTART.md](../../docs/MCP_QUICKSTART.md)
- 🐛 Troubleshooting: Ver seção em MCP_QUICKSTART.md

## Desenvolvido para Orion Ledger

**Versão**: 0.1.0  
**Status**: ✅ Production Ready (Phase 1)
