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

## Monitoramento e Métricas

### Prometheus Metrics

O servidor MCP expõe métricas no formato Prometheus através do endpoint `/metrics`.

#### Métricas Disponíveis

1. **mcp_requests_total** (Counter)
   - Total de requisições MCP processadas
   - Labels: `method`, `endpoint`, `status`
   - Exemplo: `mcp_requests_total{method="GET",endpoint="/resources",status="200"} 1523`

2. **mcp_request_duration_seconds** (Histogram)
   - Duração das requisições em segundos
   - Labels: `method`, `endpoint`
   - Buckets: 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10
   - Exemplo: `mcp_request_duration_seconds_bucket{method="POST",endpoint="/tools",le="0.1"} 145`

3. **mcp_active_connections** (Gauge)
   - Número de conexões ativas no momento
   - Exemplo: `mcp_active_connections 42`

4. **mcp_errors_total** (Counter)
   - Total de erros ocorridos
   - Labels: `endpoint`, `error_type`
   - Exemplo: `mcp_errors_total{endpoint="/tools",error_type="HTTPException"} 3`

5. **mcp_redis_operations_total** (Counter)
   - Total de operações Redis realizadas
   - Labels: `operation`, `status`
   - Exemplo: `mcp_redis_operations_total{operation="get",status="success"} 8932`

#### Configurando Prometheus

1. Adicione o servidor MCP como target no `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'mcp-server'
    static_configs:
      - targets: ['localhost:8001']
    scrape_interval: 15s
    metrics_path: '/metrics'
```

2. Exemplos de queries PromQL úteis:

```promql
# Taxa de requisições por segundo
rate(mcp_requests_total[5m])

# Latência P95
histogram_quantile(0.95, rate(mcp_request_duration_seconds_bucket[5m]))

# Taxa de erros
rate(mcp_errors_total[5m]) / rate(mcp_requests_total[5m])

# Conexões ativas médias
avg_over_time(mcp_active_connections[5m])
```

#### Integrando com Grafana

Dashboard recomendado com os seguintes painéis:
- Taxa de requisições por endpoint
- Latência P50, P95, P99
- Taxa de erros por tipo
- Conexões ativas
- Operações Redis por segundo

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
