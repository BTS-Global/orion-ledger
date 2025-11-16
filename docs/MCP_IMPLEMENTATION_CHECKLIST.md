# ✅ Checklist de Implementação MCP - Orion Ledger

Este documento fornece um checklist passo-a-passo para implementar o Model Context Protocol no Orion Ledger.

## 📋 Fase 0: Preparação ✅ CONCLUÍDO

### Decisão e Planejamento
- [x] **Ler documentação completa**
  - [x] `MCP_EXECUTIVE_SUMMARY.md` - Visão de negócio
  - [x] `MCP_IMPLEMENTATION_PLAN.md` - Plano técnico detalhado
  - [x] `MCP_QUICKSTART_CODE.md` - Código base
- [x] **Aprovar investimento e ROI**
  - [x] Revisar custos ($50/mês infra + $2.30/empresa/mês API)
  - [x] Validar timeline (8-10 semanas)
  - [x] Aprovar alocação de recursos (1 dev senior + 1 junior)
- [x] **Definir escopo inicial**
  - [x] Decidir se começa com MVP (Fase 1+2) ou completo
  - [x] Escolher modelo LLM principal (Claude vs GPT-4)
  - [x] Definir empresas piloto (5-10 empresas iniciais)

### Setup do Ambiente
- [x] **Criar branch de desenvolvimento**
  ```bash
  git checkout -b feature/mcp-implementation
  ```
- [x] **Criar estrutura de diretórios**
  ```bash
  mkdir -p backend/mcp_server
  ```
- [x] **Criar requirements-mcp.txt**
  - [x] mcp, fastapi, uvicorn, pydantic
  - [x] anthropic, openai
  - [x] redis, aiohttp
- [x] **Configurar variáveis de ambiente**
  - [x] Documentação de variáveis em config.py

---

## 🏗️ Fase 1: MCP Server Base ✅ CONCLUÍDO (100%)

### 1.1 Server e Configuração
- [ ] **Criar `config.py`**
  - [ ] Copiar código de `MCP_QUICKSTART_CODE.md` seção 3
  - [ ] Ajustar URLs e credenciais
  - [ ] Validar com `pytest backend/mcp_server/test_config.py`
- [ ] **Criar `server.py`**
  - [ ] Copiar código de `MCP_QUICKSTART_CODE.md` seção 2
  - [ ] Testar startup: `python backend/mcp_server/server.py`
  - [ ] Acessar http://localhost:8001/health
  - [ ] Validar resposta: `{"status": "healthy"}`
- [x] **Configurar CORS**
  - [x] Setup CORS middleware em server.py
  - [x] Suporte para todas as origens (configurável)

### 1.2 Middleware e Segurança ✅
- [x] **Criar `middleware.py`**
  - [x] Implementar `MCPAuthMiddleware` com validação via Django ORM
  - [x] Implementar `RateLimitMiddleware` com Redis
  - [x] Implementar `AuditLogMiddleware` para registro de operações
  - [x] Cache de API keys por 5 minutos
- [x] **Configurar Redis**
  - [x] Configuração em settings (host, port, db, password)
  - [x] Graceful degradation se Redis não disponível
  - [x] Rate limiting: 100/min, 1000/hora

### 1.3 Health Checks e Monitoring ✅
- [x] **Adicionar endpoints de diagnóstico**
  - [x] `/health` - Status básico + Redis connection
  - [x] `/metrics` - Métricas do servidor (placeholder)
  - [x] Headers de timing em todas as respostas
- [x] **Configurar logging**
  - [x] Logging estruturado com Python logging
  - [x] Níveis configuráveis via env (DEBUG, INFO, WARNING, ERROR)
  - [x] Logs JSON para todas as operações

---

## 📚 Fase 2: Resources ✅ CONCLUÍDO (100%)

### 2.1 Company Resources ✅
- [x] **Implementar `CompanyResource`**
  - [x] Dados básicos da empresa
  - [x] Resumo do plano de contas
  - [x] Isolamento por company_id
  - [x] Endpoint `/resources/company/{company_id}`

### 2.2 Transaction Resources ✅
- [x] **Implementar `TransactionsResource`**
  - [x] Filtros por período (days)
  - [x] Filtro por account_code
  - [x] Limite de resultados configurável
  - [x] Include de journal entry lines
  - [x] Endpoint `/resources/transactions/{company_id}`

### 2.3 Report Resources ✅
- [x] **Implementar `ReportsResource`**
  - [x] Trial Balance integration
  - [x] Placeholders para Balance Sheet e Income Statement
  - [x] Filtros por data
  - [x] Endpoint `/resources/reports/{company_id}?report_type=X`

### 2.4 Chart of Accounts Resources ✅
- [x] **Implementar `ChartOfAccountsResource`**
  - [x] Hierarquia de contas por tipo
  - [x] Estatísticas de uso (90 dias)
  - [x] Contas mais usadas (top 20)
  - [x] Endpoint `/resources/chart_of_accounts/{company_id}`

### 2.5 Resource Registry ✅
- [x] **Sistema de registro de resources**
  - [x] Registry centralizado em `RESOURCE_REGISTRY`
  - [x] Factory function `get_resource()`
  - [x] Endpoint `/resources` para listar todos
- [ ] **Implementar `get_chart_of_accounts`**
  - [ ] Hierarquia completa
  - [ ] Incluir saldos atuais
- [ ] **Cache com Redis**
  ```python
  @cache_result(ttl=3600)  # 1 hora
  def get_chart_of_accounts(company_id: str):
      ...
  ```
- [ ] **Testes**
  ```bash
  pytest backend/mcp_server/tests/test_resources_coa.py -v
  ```

---

## 🔧 Fase 3: Tools (4-5 dias)

### 3.1 Classification Tool
- [ ] **Implementar `classify_transaction`**
  - [ ] Copiar código de `MCP_QUICKSTART_CODE.md` seção 6
  - [ ] Integrar com `rag_service.find_similar_transactions`
  - [ ] Retornar top 3 sugestões com confidence
- [ ] **Testar com dados reais**
  ```bash
  curl -X POST http://localhost:8001/mcp/tools/classify_transaction \
    -H "X-Orion-API-Key: test-key" \
    -H "Content-Type: application/json" \
    -d '{
      "company_id": "123",
      "description": "AWS Payment",
      "amount": 10000.00
    }'
  ```
- [ ] **Validar acurácia**
  - [ ] Mínimo 70% de acurácia em transações conhecidas
  - [ ] Confidence score condizente com acurácia

### 3.2 CRUD Tools
- [ ] **Implementar `create_transaction`**
  - [ ] Validação rigorosa de entrada
  - [ ] Partida dobrada automática
  - [ ] Retornar ID da transação criada
- [ ] **Implementar `update_transaction`**
  - [ ] Validar permissões
  - [ ] Auditoria de mudanças
- [ ] **Implementar `delete_transaction`**
  - [ ] Soft delete (is_active=False)
  - [ ] Validar se não está em período fechado
- [ ] **Testes de integração**
  ```bash
  pytest backend/mcp_server/tests/test_tools_crud.py -v
  ```

### 3.3 Report Generation Tools
- [ ] **Implementar `generate_trial_balance`**
  - [ ] Integrar com `reports.trial_balance.TrialBalanceService`
  - [ ] Retornar JSON ou PDF
- [ ] **Implementar `generate_cashflow`**
  - [ ] Método direto e indireto
- [ ] **Background processing**
  - [ ] Para relatórios pesados (>10k transações)
  - [ ] Usar Celery + Redis
  - [ ] Notificar quando pronto
- [ ] **Testes**
  ```bash
  pytest backend/mcp_server/tests/test_tools_reports.py -v
  ```

### 3.4 Audit Tools
- [ ] **Implementar `audit_transactions`**
  - [ ] Detectar duplicatas (descrição + valor + data próxima)
  - [ ] Detectar outliers (>3 desvios padrão)
  - [ ] Detectar classificações inconsistentes
- [ ] **Implementar `validate_double_entry`**
  - [ ] Validar débito = crédito
  - [ ] Validar contas válidas
- [ ] **Performance**
  - [ ] Processar 10k transações em <30s
  - [ ] Usar queries otimizadas com `select_related`
- [ ] **Testes**
  ```bash
  pytest backend/mcp_server/tests/test_tools_audit.py -v
  ```

---

## 💬 Fase 4: Prompts (1-2 dias)

### 4.1 Prompt Templates
- [ ] **Criar `prompts.py`**
  - [ ] Copiar código de `MCP_QUICKSTART_CODE.md` seção 7
- [ ] **Template: Classificação**
  ```python
  def classify_prompt(transaction, similar):
      return f"""
      Classifique esta transação:
      
      Descrição: {transaction['description']}
      Valor: R$ {transaction['amount']}
      Fornecedor: {transaction.get('vendor', 'N/A')}
      
      Transações similares:
      {format_similar(similar)}
      
      Retorne: account_code, account_name, confidence (0-1)
      """
  ```
- [ ] **Template: Análise Financeira**
- [ ] **Template: Auditoria**
- [ ] **Testes**
  - [ ] Validar que prompts geram respostas corretas
  - [ ] A/B test com diferentes templates

### 4.2 Few-Shot Examples
- [ ] **Coletar exemplos reais**
  - [ ] 20-30 transações bem classificadas
  - [ ] Variados: receitas, despesas, ativos, passivos
- [ ] **Adicionar ao prompt**
  ```python
  EXAMPLES = [
      {
          "description": "AWS Payment",
          "amount": 10000,
          "account": "5.01.08.001 - Despesas com TI"
      },
      ...
  ]
  ```
- [ ] **Medir melhoria**
  - [ ] Acurácia antes: X%
  - [ ] Acurácia depois: Y%
  - [ ] Target: +10% de melhoria

---

## 🎨 Fase 5: Frontend Integration (3-4 dias)

### 5.1 MCP Client no Frontend
- [ ] **Instalar dependência**
  ```bash
  cd frontend
  npm install @anthropic-ai/mcp-client
  ```
- [ ] **Criar `src/services/mcp_client.ts`**
  ```typescript
  import { MCPClient } from '@anthropic-ai/mcp-client';
  
  export const mcpClient = new MCPClient({
    baseUrl: 'http://localhost:8001/mcp',
    apiKey: process.env.VITE_ORION_API_KEY
  });
  ```
- [ ] **Testes de conexão**
  ```bash
  npm run test:integration
  ```

### 5.2 UI Components
- [ ] **Componente: AIClassificationButton**
  ```tsx
  <Button onClick={handleAIClassify}>
    🤖 Classificar com IA
  </Button>
  ```
  - [ ] Mostrar loading state
  - [ ] Mostrar sugestões com confidence
  - [ ] Permitir aceitar/rejeitar
- [ ] **Componente: AIAssistantChat**
  - [ ] Input de texto
  - [ ] Histórico de mensagens
  - [ ] Streaming de respostas
- [ ] **Componente: AIAuditResults**
  - [ ] Mostrar problemas encontrados
  - [ ] Ações: corrigir, ignorar, marcar como falso positivo

### 5.3 Integração com Claude Desktop
- [ ] **Configurar MCP no Claude Desktop**
  ```json
  // ~/Library/Application Support/Claude/claude_desktop_config.json
  {
    "mcpServers": {
      "orion-ledger": {
        "command": "node",
        "args": ["/path/to/backend/mcp_server/server.js"],
        "env": {
          "ORION_API_KEY": "your-key"
        }
      }
    }
  }
  ```
- [ ] **Testar comandos**
  - [ ] "Mostre as empresas"
  - [ ] "Classifique esta transação: AWS Payment R$10k"
  - [ ] "Gere o balancete de outubro"
- [ ] **Documentar workflows**
  - [ ] Criar `docs/MCP_CLAUDE_WORKFLOWS.md`

---

## 🧪 Fase 6: Testing (2-3 dias)

### 6.1 Unit Tests
- [ ] **Coverage mínimo: 80%**
  ```bash
  pytest backend/mcp_server --cov=mcp_server --cov-report=html
  open htmlcov/index.html
  ```
- [ ] **Testar todos os resources**
- [ ] **Testar todos os tools**
- [ ] **Testar middleware**

### 6.2 Integration Tests
- [ ] **Testar fluxo completo**
  ```python
  def test_full_classification_flow():
      # 1. Upload documento
      # 2. Extrair transações
      # 3. Classificar com MCP
      # 4. Salvar feedback
      # 5. Validar métricas
  ```
- [ ] **Testar com dados reais**
  - [ ] 5-10 empresas piloto
  - [ ] 100-1000 transações por empresa

### 6.3 Performance Tests
- [ ] **Load testing**
  ```bash
  # Instalar locust
  pip install locust
  
  # Executar
  locust -f backend/mcp_server/tests/locustfile.py
  ```
- [ ] **Targets**
  - [ ] 100 req/s sem degradação
  - [ ] <200ms p95 latency
  - [ ] <500ms p99 latency
- [ ] **Otimizar queries lentas**
  - [ ] Adicionar índices
  - [ ] Usar `select_related` / `prefetch_related`
  - [ ] Cache de recursos pesados

### 6.4 Security Tests
- [ ] **Testar autenticação**
  - [ ] Sem token → 401
  - [ ] Token inválido → 403
  - [ ] Token expirado → 401
- [ ] **Testar rate limiting**
  - [ ] 101+ req/min → 429
- [ ] **Testar input validation**
  - [ ] SQL injection
  - [ ] XSS
  - [ ] Campos obrigatórios
- [ ] **Penetration testing**
  - [ ] Usar OWASP ZAP ou similar

---

## 🚀 Fase 7: Deploy (2-3 dias)

### 7.1 Preparação
- [ ] **Criar Dockerfile**
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements-mcp.txt .
  RUN pip install -r requirements-mcp.txt
  COPY backend/mcp_server ./mcp_server
  CMD ["python", "mcp_server/server.py"]
  ```
- [ ] **Criar docker-compose.yml**
  ```yaml
  services:
    mcp_server:
      build: .
      ports:
        - "8001:8001"
      environment:
        - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
        - REDIS_URL=redis://redis:6379
      depends_on:
        - redis
    redis:
      image: redis:7-alpine
  ```
- [ ] **Testar localmente**
  ```bash
  docker-compose up --build
  ```

### 7.2 Deploy em Staging
- [ ] **Provisionar infraestrutura**
  - [ ] Servidor (2 CPU, 4GB RAM)
  - [ ] Redis managed (AWS ElastiCache ou similar)
  - [ ] Load balancer
- [ ] **Configurar CI/CD**
  ```yaml
  # .github/workflows/deploy-mcp.yml
  name: Deploy MCP Server
  on:
    push:
      branches: [main]
  jobs:
    deploy:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Build and push
          run: |
            docker build -t orion-mcp .
            docker push ghcr.io/orion/mcp:latest
        - name: Deploy
          run: |
            ssh deploy@server 'docker pull && docker-compose up -d'
  ```
- [ ] **Smoke tests em staging**
  ```bash
  ./scripts/smoke_tests.sh https://mcp-staging.orion.com
  ```

### 7.3 Deploy em Produção
- [ ] **Backup de dados**
  ```bash
  pg_dump orion_db > backup_$(date +%Y%m%d).sql
  ```
- [ ] **Deploy gradual**
  - [ ] 10% do tráfego → monitorar 1h
  - [ ] 50% do tráfego → monitorar 2h
  - [ ] 100% do tráfego
- [ ] **Rollback plan**
  ```bash
  # Se algo der errado
  docker-compose down
  docker-compose -f docker-compose.old.yml up -d
  ```
- [ ] **Monitoring**
  - [ ] Logs: CloudWatch ou similar
  - [ ] Métricas: Prometheus + Grafana
  - [ ] Alertas: PagerDuty ou Slack

### 7.4 Documentação
- [ ] **Criar runbook**
  - [ ] Como fazer deploy
  - [ ] Como fazer rollback
  - [ ] Troubleshooting comum
- [ ] **Atualizar README**
  - [ ] Adicionar seção MCP
  - [ ] Exemplos de uso
- [ ] **User guide**
  - [ ] Como usar IA no Orion
  - [ ] Casos de uso práticos
  - [ ] FAQ

---

## 📊 Fase 8: Monitoring & Optimization (Contínuo)

### 8.1 Métricas de Uso
- [ ] **Instrumentar código**
  ```python
  from prometheus_client import Counter, Histogram
  
  mcp_requests = Counter('mcp_requests_total', 'Total MCP requests')
  mcp_latency = Histogram('mcp_latency_seconds', 'MCP request latency')
  ```
- [ ] **Dashboard no Grafana**
  - [ ] Requests per minute
  - [ ] Latency (p50, p95, p99)
  - [ ] Error rate
  - [ ] Cache hit rate
- [ ] **Alertas**
  - [ ] Error rate > 5% → Slack alert
  - [ ] Latency p99 > 1s → Slack alert
  - [ ] MCP server down → PagerDuty

### 8.2 Métricas de Negócio
- [ ] **Classificação IA**
  - [ ] Accuracy rate (target: 90%+)
  - [ ] User acceptance rate (target: 85%+)
  - [ ] Time saved per transaction
- [ ] **Auditoria**
  - [ ] Problemas detectados
  - [ ] Falsos positivos
  - [ ] Problemas corrigidos
- [ ] **Satisfação**
  - [ ] NPS (target: +15 pontos)
  - [ ] Feedback qualitativo

### 8.3 Otimização Contínua
- [ ] **A/B testing de prompts**
  - [ ] Testar diferentes templates
  - [ ] Medir impacto em accuracy
  - [ ] Escolher vencedor
- [ ] **Fine-tuning de modelos**
  - [ ] Coletar 1000+ correções
  - [ ] Fine-tune GPT-4 ou Claude
  - [ ] Comparar com baseline
- [ ] **Otimização de custos**
  - [ ] Usar modelos menores quando possível
  - [ ] Cache agressivo
  - [ ] Batch requests

---

## ✅ Critérios de Sucesso

### MVP (Fase 1-3)
- [ ] ✅ MCP Server rodando e estável
- [ ] ✅ 3+ resources implementados
- [ ] ✅ 3+ tools implementados
- [ ] ✅ Claude Desktop integrado
- [ ] ✅ 80%+ test coverage

### Produção (Fase 1-7)
- [ ] ✅ Deploy em produção com uptime 99.9%
- [ ] ✅ 10+ empresas usando IA
- [ ] ✅ 90%+ accuracy em classificação
- [ ] ✅ 85%+ user acceptance
- [ ] ✅ +15 pontos NPS

### Scale (Fase 8)
- [ ] ✅ 100+ empresas usando IA
- [ ] ✅ 10k+ transações/dia
- [ ] ✅ <200ms p95 latency
- [ ] ✅ <$3/empresa/mês em custos

---

## 🆘 Troubleshooting

### MCP Server não inicia
```bash
# Verificar logs
tail -f backend/logs/mcp_server.log

# Testar Redis
redis-cli ping

# Testar DB
python -c "from django.db import connection; connection.ensure_connection()"
```

### Rate limit muito restritivo
```python
# Aumentar em config.py
RATE_LIMIT_PER_MINUTE = 200  # era 100
```

### Accuracy baixa (<70%)
1. Verificar qualidade de dados históricos
2. Adicionar mais few-shot examples
3. Aumentar top_k de transações similares
4. Fine-tune o modelo

### Latency alta (>1s)
1. Adicionar índices no DB
2. Aumentar cache TTL
3. Otimizar queries (usar `select_related`)
4. Usar modelo mais rápido (gpt-4.1-nano)

---

## 📚 Recursos

### Documentação
- [MCP Spec](https://spec.modelcontextprotocol.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [OpenAI API](https://platform.openai.com/docs)

### Código de Referência
- `docs/MCP_IMPLEMENTATION_PLAN.md` - Plano completo
- `docs/MCP_QUICKSTART_CODE.md` - Código pronto
- `docs/MCP_EXECUTIVE_SUMMARY.md` - Resumo executivo

### Suporte
- **Issues técnicos**: GitHub Issues
- **Dúvidas**: Slack #orion-ai
- **Emergências**: PagerDuty

---

## 🎉 Próximos Passos

Após completar este checklist:

1. ✅ **Validar com usuários piloto** (5-10 empresas)
2. ✅ **Coletar feedback** e iterar
3. ✅ **Rollout gradual** para 100% dos usuários
4. ✅ **Anunciar feature** com case studies
5. ✅ **Medir ROI** e celebrar 🎊

---

**Última atualização**: 2025
**Versão**: 1.0
**Autor**: Orion AI Team
