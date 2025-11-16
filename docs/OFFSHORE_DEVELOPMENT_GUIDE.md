# Guia de Desenvolvimento: Orion para Corporate Services Offshore

**Data:** 16 de Novembro de 2025  
**Versão:** 2.0-offshore  
**Objetivo:** Transformar o Orion em sistema completo de contabilidade para corporate services

---

## 📋 Resumo Executivo

O Orion está sendo expandido de um sistema de contabilidade americano para uma plataforma completa de gestão contábil e compliance para **corporate services providers (CSPs)** que atendem **offshore entities** em múltiplas jurisdições.

### Contexto do Negócio

Você é um **corporate services provider** que:
- Atende múltiplas offshore companies (BVI, Cayman, Seychelles, etc.)
- Precisa gerenciar contabilidade, compliance e deadlines
- Necessita suporte multi-moeda
- Deve cumprir Economic Substance Requirements
- Precisa rastrear annual returns e government fees
- Gerencia KYC/Due Diligence de clientes

---

## ✅ O Que Foi Implementado

### 1. Modelo de Empresa Expandido (`Company`)

**Novos Campos:**

```python
# Jurisdição e Tipo de Entidade
jurisdiction = CharField  # BVI, Cayman, Seychelles, etc.
entity_type = CharField   # IBC, LLC, Foundation, Trust, etc.

# Detalhes de Incorporação
incorporation_date = DateField
registration_number = CharField
currency = CharField  # Moeda principal (USD, EUR, etc.)

# Registered Agent/Office
registered_agent_name = CharField
registered_agent_address = TextField

# Corporate Services Tracking
client_reference = CharField
annual_renewal_date = DateField
annual_fee = DecimalField

# Status
is_active = BooleanField
notes = TextField
```

**Métodos Helper:**
- `is_offshore()` - Verifica se é jurisdição offshore
- `is_us_entity()` - Verifica se é entidade US
- `days_until_renewal()` - Calcula dias até renewal

### 2. Chart of Accounts Multi-Moeda

**Novos Campos:**

```python
currency = CharField  # Moeda específica da conta
allow_multi_currency = BooleanField  # Permite múltiplas moedas
tax_reporting_category = CharField  # Categoria para reporting
```

### 3. Novos Modelos Offshore

#### `AnnualReturn`
Gestão de Annual Returns para offshore entities:
- Filing year, due date, status
- Resumo financeiro (assets, liabilities, equity, net income)
- Upload de documentos (PDF, supporting docs)
- Tracking de reference numbers

#### `EconomicSubstanceReport`
Economic Substance Reporting (ES):
- Business activity type (Banking, Insurance, Fund Management, Holding, etc.)
- Substance requirements:
  - Adequate employees (número)
  - Adequate premises (endereço)
  - Adequate expenditure (valor)
  - Core activities conducted locally
- Assessment de compliance
- PDF generation

#### `JurisdictionFee`
Tracking de taxas por jurisdição:
- Fee types: Annual renewal, Government, Registered Agent, etc.
- Amount, currency, due date
- Payment tracking
- Overdue alerts

#### `ExchangeRate`
Taxas de câmbio históricas:
- From/to currency pairs
- Historical rates
- Methods: `get_rate()`, `convert()`
- Suporte para conversão automática

#### `CorporateServiceClient`
Gestão de clientes CSP:
- Client reference, type (Individual, Company, Trust, etc.)
- Contact details
- KYC/Due Diligence tracking
- Risk rating (Low, Medium, High)
- Relationship manager assignment
- Status (Prospect, Active, Inactive, Terminated)

### 4. Jurisdições Suportadas

**Caribbean Offshore:**
- 🇻🇬 BVI (British Virgin Islands)
- 🇰🇾 Cayman Islands
- 🇧🇸 Bahamas
- 🇸🇨 Seychelles
- 🇵🇦 Panama
- 🇧🇿 Belize
- E mais 6 jurisdições caribenhas

**Outras Regiões:**
- 🇺🇸 United States
- 🇨🇦 Canada
- 🇬🇧 UK, 🇮🇪 Ireland, 🇱🇺 Luxembourg, 🇲🇹 Malta, 🇨🇾 Cyprus
- 🇧🇷 Brazil, 🇺🇾 Uruguay
- 🇸🇬 Singapore, 🇭🇰 Hong Kong

### 5. Tipos de Entidade

**US Entities:**
- US LLC, C-Corp, S-Corp, Partnership, Sole Proprietorship

**Offshore:**
- IBC (International Business Company)
- Foundation
- Trust
- Limited Company
- Exempted Company
- Offshore LLC

**Brazil:**
- LTDA (Sociedade Limitada)
- S.A. (Sociedade Anônima)
- EIRELI

---

## 🚀 Próximos Passos de Desenvolvimento

### Fase 1: API e Serializers (1 semana)

**Tarefas:**
- [ ] Criar serializers para novos modelos offshore
- [ ] Criar ViewSets REST para:
  - AnnualReturn (CRUD + generate PDF)
  - EconomicSubstanceReport (CRUD + assessment)
  - JurisdictionFee (CRUD + overdue alerts)
  - ExchangeRate (CRUD + conversion endpoint)
  - CorporateServiceClient (CRUD + KYC tracking)
- [ ] Atualizar Company ViewSet com novos campos
- [ ] Criar endpoint para conversão de moeda

**Exemplo de endpoints:**
```
GET/POST    /api/offshore/annual-returns/
GET         /api/offshore/annual-returns/{id}/
POST        /api/offshore/annual-returns/{id}/generate-pdf/
GET         /api/offshore/annual-returns/?company={id}&status=OVERDUE

GET/POST    /api/offshore/es-reports/
POST        /api/offshore/es-reports/{id}/assess/

GET/POST    /api/offshore/fees/
GET         /api/offshore/fees/overdue/?company={id}

GET/POST    /api/offshore/exchange-rates/
POST        /api/offshore/exchange-rates/convert/
  Body: {amount, from_currency, to_currency, date}

GET/POST    /api/offshore/clients/
GET         /api/offshore/clients/{id}/companies/
GET         /api/offshore/clients/{id}/kyc-review-due/
```

### Fase 2: Frontend - Páginas Offshore (2 semanas)

**Nova Navegação:**
```
Dashboard
  ├─ Corporate Services Dashboard (NOVO)
  │   ├─ Clientes overview
  │   ├─ Companies por jurisdição
  │   ├─ Upcoming renewals
  │   └─ Overdue items
  │
├─ Companies
│   └─ Adicionar filtros por jurisdiction e entity_type
│
├─ Offshore (NOVO)
│   ├─ Annual Returns
│   ├─ Economic Substance Reports
│   ├─ Jurisdiction Fees
│   └─ Renewal Calendar
│
├─ Clients (NOVO)
│   ├─ Client List
│   ├─ KYC Review Dashboard
│   └─ Risk Assessment
│
└─ Settings
    └─ Exchange Rates Management
```

**Componentes a Criar:**

1. **`OffshoreOverview.tsx`** - Dashboard principal para CSP
   - Cards: Total clients, Active companies, Upcoming renewals, Overdue fees
   - Chart: Companies by jurisdiction
   - Table: Next 10 upcoming deadlines

2. **`AnnualReturnsPage.tsx`**
   - List view com filtros (company, year, status)
   - Create/Edit form
   - PDF generation
   - Status tracking

3. **`EconomicSubstancePage.tsx`**
   - Wizard form para ES reporting
   - Substance requirements checklist
   - Assessment calculator
   - PDF generation

4. **`JurisdictionFeesPage.tsx`**
   - Calendar view de fees
   - Overdue alerts
   - Payment tracking
   - Bulk payment recording

5. **`ClientsPage.tsx`**
   - Client list com KYC status
   - Risk rating badges
   - Companies por cliente
   - KYC review reminders

6. **`RenewalCalendarPage.tsx`**
   - Calendar view (month/year)
   - Color-coded by status
   - Quick actions (mark as paid, snooze)

### Fase 3: Business Logic & Automation (1 semana)

**Tarefas:**

1. **Celery Tasks para Automação:**
   ```python
   @shared_task
   def check_overdue_annual_returns():
       """Check e envia alertas para annual returns overdue"""
   
   @shared_task
   def check_upcoming_renewals():
       """Alerta renewals nos próximos 30 dias"""
   
   @shared_task
   def check_kyc_review_due():
       """Alerta KYC reviews que vencem em breve"""
   
   @shared_task
   def update_exchange_rates():
       """Fetch rates de API externa (exchangerate-api.com)"""
   ```

2. **Email Notifications:**
   - Annual return due (30, 15, 7 dias antes)
   - Renewal due
   - Fee overdue
   - KYC review due

3. **Auto-generate Annual Returns:**
   - Criar draft de annual return automaticamente
   - Preencher valores financeiros do sistema
   - Marcar para revisão

4. **Exchange Rate Integration:**
   - Integrar com exchangerate-api.com (free tier)
   - Atualizar rates diariamente
   - Fallback para rates manuais

### Fase 4: Reports & PDF Generation (1 semana)

**Templates PDF a Criar:**

1. **Annual Return PDF** (por jurisdição)
   - BVI template
   - Cayman template
   - Seychelles template
   - Generic template

2. **Economic Substance Report PDF**
   - Standardized format
   - Checklist visual
   - Supporting evidence section

3. **Multi-Company Report**
   - Consolidated view de múltiplas entities
   - Group by jurisdiction
   - Currency conversion

4. **Client Portfolio Report**
   - Todas companies de um cliente
   - Status geral
   - Upcoming obligations

### Fase 5: Multi-Currency Integration (1 semana)

**Tarefas:**

1. **Transaction Currency:**
   - Adicionar campo `currency` em Transaction
   - Converter para currency da company em reports
   - Track forex gains/losses

2. **Report Currency Selection:**
   - User pode escolher currency para viewing reports
   - Real-time conversion
   - Historical rate usado (transaction date)

3. **Consolidated Reports Multi-Currency:**
   - Select base currency
   - Convert all company balances
   - Show exchange rate used

### Fase 6: KYC/Compliance Module (1 semana)

**Tarefas:**

1. **KYC Document Management:**
   - Upload docs (passport, proof of address, etc.)
   - Document expiry tracking
   - Auto-reminders para renewal

2. **Due Diligence Questionnaires:**
   - Template forms por tipo de cliente
   - Electronic signature
   - Version control

3. **Risk Assessment Calculator:**
   - Score based em:
     - Country risk
     - Business type
     - Transaction volume
     - PEP status
   - Auto-update risk rating

4. **Audit Trail:**
   - Log todas actions de compliance
   - Immutable records
   - Export para authorities

---

## 📚 Fluxos de Trabalho Típicos

### Fluxo 1: Onboarding de Novo Cliente Offshore

1. **Create Client** (`CorporateServiceClient`)
   - Fill basic info
   - Assign relationship manager
   - Set risk rating

2. **KYC Collection**
   - Upload documents
   - Complete questionnaire
   - Review and approve

3. **Create Company** (`Company`)
   - Select jurisdiction
   - Set entity type
   - Link to client

4. **Setup COA**
   - Use offshore template
   - Customize se necessário

5. **Schedule Obligations**
   - Create first annual return (draft)
   - Set renewal date
   - Add government fees

### Fluxo 2: Annual Return Filing

1. **System Auto-Creates Draft** (30 dias antes due date)
   - Pulls financial data
   - Creates draft annual return

2. **Accountant Reviews**
   - Verify numbers
   - Add notes
   - Mark as PENDING

3. **Manager Approves**
   - Review
   - Generate PDF
   - Mark as APPROVED

4. **Filing**
   - Submit to registry (manual or API)
   - Upload confirmation
   - Enter reference number
   - Mark as FILED

### Fluxo 3: Economic Substance Assessment

1. **Create ES Report**
   - Select business activity
   - Answer substance questions

2. **Collect Evidence**
   - Upload employment contracts
   - Upload lease agreement
   - Upload expense receipts

3. **Assessment**
   - System calculates if meets requirements
   - Generates recommendations

4. **Submit Report**
   - Generate PDF
   - Submit to authority
   - Track submission status

---

## 🔧 Comandos Úteis

### Backend

```bash
# Criar migrations
python manage.py makemigrations

# Aplicar migrations (quando DB estiver disponível)
python manage.py migrate

# Populate sample exchange rates
python manage.py populate_offshore_templates

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver 8000

# Run Celery worker
celery -A backend worker -l info

# Run Celery beat (para scheduled tasks)
celery -A backend beat -l info
```

### Frontend

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

---

## 📊 Exemplo de Dados

### Offshore Company Example

```python
company = Company.objects.create(
    name="Caribbean Trading Ltd",
    jurisdiction="BVI",
    entity_type="IBC",
    tax_id="2123456",
    registration_number="2123456",
    incorporation_date="2023-01-15",
    fiscal_year_start="2024-01-01",
    address="P.O. Box 3444",
    city="Road Town",
    state="Tortola",
    country="British Virgin Islands",
    currency="USD",
    registered_agent_name="BVI Corporate Services Ltd",
    registered_agent_address="123 Main Street, Road Town, Tortola",
    annual_renewal_date="2025-01-15",
    annual_fee=1500.00,
    client_reference="CLI-001",
    is_active=True,
    owner=user
)
```

### Annual Return Example

```python
annual_return = AnnualReturn.objects.create(
    company=company,
    filing_year=2024,
    due_date="2025-05-31",
    status="PENDING",
    total_assets=250000.00,
    total_liabilities=50000.00,
    total_equity=200000.00,
    net_income=75000.00,
    created_by=user
)
```

---

## 🎯 Métricas de Sucesso

Após implementação completa, o sistema deve suportar:

- ✅ **50+ offshore companies** simultâneas
- ✅ **10+ jurisdictions** diferentes
- ✅ **Multi-currency** accounting
- ✅ **Automated reminders** (email/dashboard)
- ✅ **PDF generation** para all compliance docs
- ✅ **KYC tracking** com audit trail
- ✅ **Economic Substance** assessment
- ✅ **Consolidated reports** cross-jurisdiction

---

## 📞 Próximos Passos Imediatos

1. **Aplicar migrations** (quando DB disponível):
   ```bash
   python manage.py migrate
   ```

2. **Populate sample data**:
   ```bash
   python manage.py populate_offshore_templates
   ```

3. **Testar Django Admin**:
   - Acesse `/admin/`
   - Verifique novos modelos offshore
   - Crie sample companies offshore

4. **Começar API development**:
   - Ver Fase 1 acima
   - Criar `serializers.py` no app offshore
   - Criar `views.py` com ViewSets
   - Adicionar URLs

---

**Desenvolvido com ❤️ para Corporate Services Providers**
**Orion Ledger v2.0-offshore**
