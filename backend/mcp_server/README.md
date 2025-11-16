# Orion Ledger MCP Server

## Visão Geral

O MCP (Model Context Protocol) Server fornece uma interface padronizada para que LLMs (Large Language Models) acessem dados estruturados do sistema Orion Ledger e executem operações contábeis de forma inteligente.

## Arquitetura

```
┌─────────────┐
│   LLM       │  (Claude, GPT-4, etc.)
│   Client    │
└──────┬──────┘
       │ MCP Protocol
       │
┌──────▼──────────────────────────────┐
│   FastAPI MCP Server                │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │Resources │  │  Tools   │       │
│  └──────────┘  └──────────┘       │
│                                     │
│  ┌──────────┐  ┌──────────┐       │
│  │ Prompts  │  │Middleware│       │
│  └──────────┘  └──────────┘       │
└─────────────────┬───────────────────┘
                  │
       ┌──────────┴──────────┐
       │                     │
┌──────▼──────┐    ┌─────────▼────────┐
│   Django    │    │      Redis       │
│   Backend   │    │   (Cache/RL)     │
└─────────────┘    └──────────────────┘
```

## Componentes

### 1. Resources (Dados Estruturados)
- **company**: Informações da empresa
- **chart_of_accounts**: Plano de contas com hierarquia
- **transactions**: Transações com filtros avançados
- **reports**: Relatórios financeiros (balancete, DRE, balanço)

### 2. Tools (Funções Executáveis)
- **classify_transaction**: Classifica transação usando IA + contexto histórico
- **create_journal_entry**: Cria lançamento contábil com validação
- **audit_transactions**: Analisa transações para identificar anomalias

### 3. Prompts (Templates Reutilizáveis)
- **monthly_financial_analysis**: Análise financeira mensal
- **batch_classification**: Classificação em lote
- **accounting_assistant**: Assistente contábil geral
- **audit_report**: Relatório de auditoria
- **document_analysis**: Análise de documentos (NF, recibos)
- **custom_report**: Relatórios personalizados

### 4. Middleware
- **MCPAuthMiddleware**: Autenticação via API key
- **RateLimitMiddleware**: Limites de taxa (por minuto/hora)
- **AuditLogMiddleware**: Log de auditoria de todas as operações
- **CORS**: Configuração de CORS

## Instalação

### Dependências

```bash
# Instalar dependências do MCP
pip install -r requirements-mcp.txt
```

### Configuração

Crie/edite `.env` com as configurações:

```bash
# MCP Server
MCP_HOST=0.0.0.0
MCP_PORT=8001
MCP_DEBUG=False
MCP_LOG_LEVEL=INFO

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB_MCP=1
REDIS_PASSWORD=

# LLM APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Rate Limiting
MCP_RATE_LIMIT_PER_MINUTE=100
MCP_RATE_LIMIT_PER_HOUR=1000
```

### Iniciar o Servidor

```bash
# Método 1: Script shell
chmod +x run_mcp_server.sh
./run_mcp_server.sh

# Método 2: Python direto
python -m mcp_server.server

# Método 3: Uvicorn
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8001
```

## Uso

### 1. Autenticação

Todas as requisições (exceto `/health` e `/metrics`) requerem autenticação:

```bash
curl -H "X-MCP-API-Key: sua-api-key" \
     http://localhost:8001/resources
```

### 2. Listar Recursos Disponíveis

```bash
curl http://localhost:8001/resources
```

### 3. Acessar Dados da Empresa

```bash
curl -H "X-MCP-API-Key: sua-api-key" \
     http://localhost:8001/resources/company/company-uuid
```

### 4. Obter Plano de Contas

```bash
curl -H "X-MCP-API-Key: sua-api-key" \
     http://localhost:8001/resources/chart_of_accounts/company-uuid
```

### 5. Classificar Transação

```bash
curl -X POST \
     -H "X-MCP-API-Key: sua-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "company_id": "company-uuid",
       "description": "Compra de material de escritório",
       "amount": 150.00,
       "date": "2024-01-15",
       "vendor": "Papelaria Silva"
     }' \
     http://localhost:8001/tools/classify_transaction
```

### 6. Executar Auditoria

```bash
curl -X POST \
     -H "X-MCP-API-Key: sua-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "company_id": "company-uuid",
       "start_date": "2024-01-01",
       "end_date": "2024-01-31",
       "check_duplicates": true,
       "check_unusual_amounts": true,
       "check_inconsistencies": true
     }' \
     http://localhost:8001/tools/audit_transactions
```

## Integração com Claude Desktop

Adicione ao arquivo de configuração do Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "orion-ledger": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "env": {
        "MCP_HOST": "localhost",
        "MCP_PORT": "8001",
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

## Monitoramento

### Health Check

```bash
curl http://localhost:8001/health
```

### Métricas

```bash
curl http://localhost:8001/metrics
```

## Segurança

- **Autenticação**: Todas as operações requerem API key válida
- **Isolamento**: Cada empresa só pode acessar seus próprios dados
- **Rate Limiting**: Limites por minuto (100) e hora (1000)
- **Audit Log**: Todas as operações são registradas
- **Redis**: Cache e controle de rate limiting

## Performance

- **Caching**: Embeddings e classificações são cacheados por 1 hora
- **Batch Processing**: Suporte para classificação em lote
- **Streaming**: Suporte para respostas em streaming (próxima fase)
- **Async**: Todas as operações são assíncronas

## Desenvolvimento

### Estrutura de Arquivos

```
mcp_server/
├── __init__.py           # Inicialização do módulo
├── server.py             # FastAPI app e endpoints
├── config.py             # Configurações e settings
├── middleware.py         # Auth, rate limit, audit
├── resources.py          # Recursos MCP (dados)
├── tools.py              # Tools MCP (funções)
└── prompts.py            # Prompt templates
```

### Adicionar Novo Resource

```python
# Em resources.py
class MyNewResource(MCPResource):
    def to_dict(self) -> Dict[str, Any]:
        # Implementar lógica
        return {"data": "..."}

# Registrar
RESOURCE_REGISTRY["my_resource"] = MyNewResource
```

### Adicionar Nova Tool

```python
# Em tools.py
class MyToolParams(BaseModel):
    param1: str
    param2: int

async def my_tool_function(params: MyToolParams):
    # Implementar lógica
    return {"success": True}

# Registrar
TOOL_REGISTRY["my_tool"] = {
    "function": my_tool_function,
    "params": MyToolParams,
    "description": "Descrição da tool"
}
```

## Roadmap

- [x] Fase 1: Setup e Infraestrutura
- [ ] Fase 2: Recursos básicos (company, COA, transactions)
- [ ] Fase 3: Tools de classificação e criação
- [ ] Fase 4: Prompt templates
- [ ] Fase 5: Streaming e multi-LLM
- [ ] Fase 6: Monitoring e observabilidade
- [ ] Fase 7: Deploy em produção

## Suporte

Para issues ou dúvidas:
- Consulte a documentação completa: `docs/MCP_IMPLEMENTATION_PLAN.md`
- Abra uma issue no repositório
- Entre em contato com o time de desenvolvimento

## Licença

MIT License - Orion Ledger 2024
