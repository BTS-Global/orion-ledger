# 🚀 Guia Rápido: Iniciar MCP Server

## TL;DR - Comandos Rápidos

```bash
# 1. Instalar dependências
cd backend
pip install -r requirements-mcp.txt

# 2. Aplicar migrations
python3 manage.py migrate core

# 3. Criar API key (Python shell)
python3 manage.py shell
>>> from companies.models import Company
>>> from core.models import APIKey
>>> company = Company.objects.first()
>>> api_key = APIKey.objects.create(
...     company=company,
...     name="Dev Key",
...     can_classify=True,
...     can_audit=True
... )
>>> print(api_key.key)
>>> exit()

# 4. Iniciar servidor
./run_mcp_server.sh

# 5. Testar (em outro terminal)
curl http://localhost:8001/health
```

---

## ✅ Pré-requisitos

- [x] Python 3.8+
- [x] Django instalado
- [x] Banco de dados configurado
- [ ] Redis instalado (opcional, mas recomendado)

### Instalar Redis (opcional)

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# Testar
redis-cli ping  # deve retornar PONG
```

---

## 📋 Passo a Passo Detalhado

### 1. Configurar Ambiente

Crie/edite o arquivo `.env`:

```bash
# MCP Server
MCP_HOST=0.0.0.0
MCP_PORT=8001
MCP_DEBUG=True
MCP_LOG_LEVEL=INFO

# Redis (se disponível)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB_MCP=1

# LLM APIs (obtenha suas chaves)
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

### 2. Instalar Dependências

```bash
cd /Users/theolamounier/code/orion-ledger/backend
pip install -r requirements-mcp.txt
```

**Dependências instaladas:**
- `mcp>=0.9.0` - Model Context Protocol
- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `pydantic>=2.5.0` - Data validation
- `anthropic>=0.18.0` - Claude API
- `openai>=1.12.0` - GPT API
- `redis>=5.0.0` - Cache/rate limiting
- `aiohttp>=3.9.0` - Async HTTP

### 3. Aplicar Migrations

```bash
python3 manage.py migrate core
```

Isso cria as tabelas:
- `core_apikey` - API keys para autenticação
- `core_aiprediction` - Armazena predições da IA
- Atualiza `core_auditlog` - Adiciona campos MCP

### 4. Criar API Key

**Opção A: Django Shell**

```bash
python3 manage.py shell
```

```python
from companies.models import Company
from core.models import APIKey

# Listar empresas disponíveis
Company.objects.values_list('id', 'name')

# Escolher uma empresa
company = Company.objects.get(id='uuid-da-empresa')
# OU
company = Company.objects.first()

# Criar API key
api_key = APIKey.objects.create(
    company=company,
    name="Development Key",
    can_read=True,
    can_write=True,
    can_classify=True,
    can_audit=True
)

print(f"✅ API Key criada: {api_key.key}")
print(f"   Company: {company.name}")
print(f"   Company ID: {company.id}")
```

**Opção B: Django Admin**

1. Acesse: `http://localhost:8000/admin/`
2. Login com superuser
3. Vá em **Core → API Keys**
4. Clique em **Add API key**
5. Preencha:
   - Name: "Development Key"
   - Company: Escolha uma empresa
   - Marque: `can_read`, `can_classify`, `can_audit`
6. Salve
7. Copie a chave gerada

### 5. Iniciar o Servidor

**Opção A: Script (Recomendado)**

```bash
cd backend
./run_mcp_server.sh
```

**Opção B: Python direto**

```bash
cd backend
python3 -m mcp_server.server
```

**Opção C: Uvicorn com reload**

```bash
cd backend
uvicorn mcp_server.server:app --host 0.0.0.0 --port 8001 --reload
```

**Saída esperada:**

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### 6. Testar o Servidor

Abra um **novo terminal** e execute:

```bash
# Health check (sem autenticação)
curl http://localhost:8001/health

# Deve retornar:
# {"status":"healthy","service":"mcp-server","version":"0.1.0","redis":"connected"}

# Listar recursos (com autenticação)
curl -H "X-MCP-API-Key: orion_mcp_SUA_KEY_AQUI" \
     http://localhost:8001/resources

# Listar tools
curl -H "X-MCP-API-Key: orion_mcp_SUA_KEY_AQUI" \
     http://localhost:8001/tools

# Listar prompts
curl http://localhost:8001/prompts

# Listar modelos suportados
curl http://localhost:8001/models
```

### 7. Acessar Documentação Interativa

Abra no navegador:

**http://localhost:8001/docs**

Você verá a **Swagger UI** com todos os endpoints!

---

## 🎯 Exemplos de Uso

### Exemplo 1: Obter Dados da Empresa

```bash
curl -X GET \
  -H "X-MCP-API-Key: orion_mcp_SUA_KEY_AQUI" \
  "http://localhost:8001/resources/company/UUID_DA_EMPRESA"
```

### Exemplo 2: Obter Plano de Contas

```bash
curl -X GET \
  -H "X-MCP-API-Key: orion_mcp_SUA_KEY_AQUI" \
  "http://localhost:8001/resources/chart_of_accounts/UUID_DA_EMPRESA"
```

### Exemplo 3: Listar Transações (últimos 30 dias)

```bash
curl -X GET \
  -H "X-MCP-API-Key: orion_mcp_SUA_KEY_AQUI" \
  "http://localhost:8001/resources/transactions/UUID_DA_EMPRESA?days=30&limit=50"
```

### Exemplo 4: Classificar uma Transação

```bash
curl -X POST \
  -H "X-MCP-API-Key: orion_mcp_SUA_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "UUID_DA_EMPRESA",
    "description": "Compra de material de escritório",
    "amount": 150.00,
    "date": "2024-01-15",
    "vendor": "Papelaria Silva"
  }' \
  "http://localhost:8001/tools/classify_transaction"
```

### Exemplo 5: Criar Journal Entry

```bash
curl -X POST \
  -H "X-MCP-API-Key: orion_mcp_SUA_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "UUID_DA_EMPRESA",
    "date": "2024-01-15",
    "description": "Pagamento de fornecedor",
    "lines": [
      {
        "account_code": "2001",
        "debit": 1000.00,
        "credit": 0,
        "description": "Fornecedores"
      },
      {
        "account_code": "1001",
        "debit": 0,
        "credit": 1000.00,
        "description": "Caixa"
      }
    ]
  }' \
  "http://localhost:8001/tools/create_journal_entry"
```

### Exemplo 6: Auditar Transações

```bash
curl -X POST \
  -H "X-MCP-API-Key: orion_mcp_SUA_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "UUID_DA_EMPRESA",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "check_duplicates": true,
    "check_unusual_amounts": true,
    "check_inconsistencies": true
  }' \
  "http://localhost:8001/tools/audit_transactions"
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'mcp_server'"

**Solução:**

```bash
# Certifique-se de estar no diretório backend/
cd backend
python3 -m mcp_server.server
```

### Erro: "Connection to Redis failed"

**Opções:**

1. **Instalar e iniciar Redis** (recomendado)
2. **Continuar sem Redis** (rate limiting desabilitado)

O servidor irá degradar gracefully se Redis não estiver disponível.

### Erro: "X-MCP-API-Key header missing"

Você precisa criar uma API key primeiro (passo 4).

### Erro: "Company not found"

Certifique-se de que:
- A empresa existe no banco de dados
- O `company_id` na requisição está correto
- A API key pertence a essa empresa

### Porta 8001 já está em uso

```bash
# Mudar porta no .env
MCP_PORT=8002

# OU parar processo existente
lsof -ti:8001 | xargs kill -9
```

---

## 📊 Verificar Logs

### Logs do Servidor

Servidor roda em foreground, logs aparecem no terminal.

### Logs de Auditoria (Django Shell)

```python
from core.models import AuditLog

# Últimos 10 logs MCP
logs = AuditLog.objects.filter(service='mcp-server').order_by('-timestamp')[:10]

for log in logs:
    print(f"{log.timestamp} | {log.method} {log.path} | {log.status_code} | {log.duration_ms}ms")
```

### Logs de Predições

```python
from core.models import AIPrediction

# Últimas predições
predictions = AIPrediction.objects.order_by('-created_at')[:10]

for pred in predictions:
    print(f"{pred.created_at} | {pred.predicted_account} | confidence: {pred.confidence:.2f}")
```

---

## 🔄 Parar o Servidor

```bash
# Se rodando em foreground
Ctrl+C

# Se rodando em background
pkill -f "uvicorn mcp_server.server"
```

---

## 📚 Próximos Passos

- ✅ **Testar todos os endpoints**: Use Swagger UI em `/docs`
- ✅ **Integrar com Claude Desktop**: Ver `backend/mcp_server/README.md`
- ✅ **Criar mais API keys**: Para diferentes empresas ou ambientes
- ✅ **Monitorar logs**: Verificar audit logs no Django admin
- ✅ **Configurar rate limiting**: Ajustar limites em `.env` se necessário

---

## 💡 Dicas

1. **Use Swagger UI** (`/docs`) para explorar a API interativamente
2. **Salve sua API key** em um gerenciador de senhas
3. **Ative Redis** para melhor performance e rate limiting
4. **Configure logs** para arquivo em produção
5. **Use `DEBUG=False`** em produção

---

## 📖 Documentação Completa

- **README MCP**: `backend/mcp_server/README.md`
- **Plano Completo**: `docs/MCP_IMPLEMENTATION_PLAN.md`
- **Fase 1 Completa**: `docs/MCP_PHASE1_COMPLETE.md`
- **Checklist**: `docs/MCP_IMPLEMENTATION_CHECKLIST.md`

---

**Desenvolvido para Orion Ledger**  
**Versão**: 0.1.0  
**Status**: ✅ Operacional
