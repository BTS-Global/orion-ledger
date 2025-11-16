# Roadmap v1.1: EUA Perfeito - Orion Universal Ledger

**Foco Absoluto:** Sistema de Contabilidade para Empresas Americanas - Perfeição  
**Desenvolvimento:** 100% no Manus  
**Hospedagem:** 100% no Manus  
**Data:** 24 de Outubro de 2025  
**Autor:** Manus AI

---

## 1. Visão v1.1

Transformar o MVP atual em um **sistema de contabilidade americano de classe mundial**, superando QuickBooks, Xero e FreshBooks em funcionalidades específicas para:

- Small businesses (LLCs, S-Corps, C-Corps)
- Foreign-owned US companies
- Freelancers e contractors
- Startups

**Offshore, Brasil e outras jurisdições ficam para v2.0+**

---

## 2. Estado Atual (Base Sólida)

### ✅ Já Implementado e Funcional:

**Core:**
- Gestão multi-empresa
- Contabilidade de dupla entrada
- Plano de contas customizável
- Autenticação OAuth (Google, Microsoft)

**Documentos:**
- Upload de PDF, CSV, imagens
- OCR com Tesseract
- Extração inteligente com OpenAI
- Processamento assíncrono (Celery)

**Relatórios:**
- Balance Sheet
- Income Statement
- Cash Flow
- Export para Excel e PDF

**Formulários IRS:**
- Form 5472
- Form 1099-NEC
- Form 1120
- Form 1040

**Frontend:**
- Interface moderna (React + TypeScript)
- Componentes reutilizáveis (shadcn/ui)
- **Dashboard com KPIs e gráficos interativos (NOVO)**
- **Tooltips e help text em páginas-chave (NOVO)**

**Performance:**
- **Cache Redis para KPIs (NOVO)**

---

## 3. Roadmap v1.1: Perfeição EUA

### Fase 1: Polish & Performance (2-3 semanas)

**Objetivo:** Refinar o que já existe, corrigir bugs, melhorar UX.

**Entregáveis:**

**1.1. Refinamento de UX/UI**
- [x] ~~Revisar e melhorar todos os fluxos de usuário~~
- [x] **Adicionar tooltips e help text em campos complexos (CONCLUÍDO)**
- [ ] Melhorar feedback visual (loading states, error messages)
- [ ] Adicionar empty states mais informativos
- [ ] Implementar onboarding interativo para novos usuários
- [ ] Adicionar tour guiado (react-joyride)

**1.2. Performance**
- [ ] Otimizar queries do banco (add indexes, select_related, prefetch_related)
- [ ] Implementar paginação em todas as listas
- [x] **Adicionar cache (Redis) para relatórios frequentes (CONCLUÍDO - para KPIs)**
- [ ] Otimizar processamento de documentos (paralelização)
- [ ] Lazy loading de imagens e componentes pesados

**1.3. Testes e Qualidade**
- [ ] Aumentar cobertura de testes para 80%+
- [ ] Adicionar testes E2E com Playwright
- [ ] Implementar testes de performance (Locust)
- [ ] Code review completo
- [ ] Refatoração de código duplicado

**1.4. Documentação**
- [x] **Atualizar README com instruções claras (CONCLUÍDO - via documentação de fase)**
- [ ] Criar guia do usuário completo
- [ ] Documentar API com Swagger
- [ ] Criar vídeos tutoriais (Loom)

---

### Fase 2: Funcionalidades Essenciais (3-4 semanas)

**Objetivo:** Adicionar funcionalidades críticas que faltam para competir com QuickBooks.

**Entregáveis:**

**2.1. Gestão de Clientes e Fornecedores**
- [ ] Modelo `Customer` (nome, email, endereço, tax ID)
- [ ] Modelo `Vendor` (nome, email, endereço, EIN)
- [ ] CRUD completo no frontend
- [ ] Associação de transações com clientes/fornecedores
- [ ] Relatórios por cliente/fornecedor

**2.2. Invoicing (Faturamento)**
- [ ] Modelo `Invoice` (número, data, cliente, itens, total)
- [ ] Modelo `InvoiceItem` (descrição, quantidade, preço unitário)
- [ ] Geração de invoices profissionais (PDF)
- [ ] Envio de invoices por email
- [ ] Tracking de status (DRAFT, SENT, PAID, OVERDUE)
- [ ] Lembretes automáticos para invoices vencidos
- [ ] Templates customizáveis de invoice

**2.3. Bill Management (Gestão de Contas a Pagar)**
- [ ] Modelo `Bill` (fornecedor, data de vencimento, valor)
- [ ] Tracking de bills pendentes
- [ ] Alertas para bills próximos do vencimento
- [ ] Pagamento de bills (registro de pagamento)
- [ ] Relatório de contas a pagar (Accounts Payable)

**2.4. Bank Reconciliation (Conciliação Bancária)**
- [ ] Importação de extratos bancários (CSV, OFX)
- [ ] Interface de matching (transação bancária ↔ transação contábil)
- [ ] Sugestões automáticas de matching (ML básico)
- [ ] Marcação de transações como reconciliadas
- [ ] Relatório de reconciliação

**2.5. Payroll Básico (Folha de Pagamento)**
- [ ] Modelo `Employee` (nome, SSN, salário, tipo)
- [ ] Cálculo de payroll (gross pay, deductions, net pay)
- [ ] Geração de paystubs (PDF)
- [ ] Tracking de impostos sobre folha (FICA, Federal, State)
- [ ] Integração com Form 941 (Quarterly Federal Tax Return)

**2.6. Inventory Management (Gestão de Estoque)**
- [ ] Modelo `Product` (nome, SKU, preço, quantidade)
- [ ] Tracking de estoque (entrada, saída, saldo)
- [ ] Valoração de estoque (FIFO, LIFO, Average Cost)
- [ ] Alertas de estoque baixo
- [ ] Relatório de movimentação de estoque

---

### Fase 3: Formulários IRS Avançados (2-3 semanas)

**Objetivo:** Completar suite de formulários IRS para cobertura total.

**Entregáveis:**

**3.1. Novos Formulários**
- [ ] **Form 941** - Employer's Quarterly Federal Tax Return
- [ ] **Form W-2** - Wage and Tax Statement
- [ ] **Form W-3** - Transmittal of Wage and Tax Statements
- [ ] **Form 1099-MISC** - Miscellaneous Income
- [ ] **Form 1099-INT** - Interest Income
- [ ] **Form 1099-DIV** - Dividends and Distributions
- [ ] **Schedule C** - Profit or Loss from Business (Sole Proprietorship)
- [ ] **Schedule E** - Supplemental Income and Loss (Rental, etc.)
- [ ] **Form 1065** - U.S. Return of Partnership Income
- [ ] **Schedule K-1** - Partner's Share of Income

**3.2. Melhorias em Formulários Existentes**
- [ ] Validação completa de campos obrigatórios
- [ ] Cálculos automáticos (impostos, deduções)
- [ ] Preview antes de gerar PDF
- [ ] Histórico de versões (drafts)
- [ ] E-filing preparation (XML generation)

**3.3. Tax Planning Tools**
- [ ] Calculadora de impostos estimados
- [ ] Projeção de impostos para fim de ano
- [ ] Sugestões de deduções (baseadas em transações)
- [ ] Comparação de cenários (LLC vs S-Corp vs C-Corp)

---

### Fase 4: Inteligência e Automação (2-3 semanas)

**Objetivo:** Usar IA para automatizar tarefas repetitivas e fornecer insights.

**Entregáveis:**

**4.1. Categorização Inteligente**
- [ ] Melhorar prompt OpenAI para categorização
- [ ] Aprendizado com correções do usuário
- [ ] Sugestões de categorias baseadas em histórico
- [ ] Detecção automática de duplicatas

**4.2. Insights Financeiros**
- [x] **Dashboard com KPIs (revenue, expenses, profit margin, cash runway) (CONCLUÍDO)**
- [x] **Gráficos interativos (recharts) (CONCLUÍDO)**
- [ ] Análise de tendências (MoM, YoY)
- [ ] Alertas inteligentes (gastos anormais, receita baixa)
- [ ] Previsão de fluxo de caixa (próximos 3 meses)

**4.3. Assistente Virtual (Chatbot)**
- [ ] Chatbot com OpenAI para responder perguntas
  - "Qual foi minha receita em março?"
  - "Quanto devo de impostos este trimestre?"
  - "Quais são minhas maiores despesas?"
- [ ] Comandos por voz (opcional)
- [ ] Sugestões proativas

**4.4. Automação de Workflows**
- [ ] Regras automáticas (ex: "Toda transação com Stripe → Receita de Vendas")
- [ ] Recurring transactions (transações recorrentes)
- [ ] Bulk actions (aprovar/categorizar múltiplas transações)

---

### Fase 5: Integrações (2 semanas)

---

### Fase 6: Compliance e Segurança (1-2 semanas)

---

### Fase 7: Polimento Final e Lançamento (1-2 semanas)

---

## 6. Funcionalidades v1.1 (Checklist Completo)

### Core Contábil
- [x] Gestão de empresas
- [x] Plano de contas customizável
- [x] Contabilidade de dupla entrada
- [x] Transações e lançamentos
- [ ] Clientes e fornecedores
- [ ] Invoicing
- [ ] Bill management
- [ ] Bank reconciliation
- [ ] Payroll básico
- [ ] Inventory management

### Documentos
- [x] Upload de documentos
- [x] OCR e extração
- [x] Processamento assíncrono
- [ ] Categorização inteligente melhorada
- [ ] Detecção de duplicatas

### Relatórios
- [x] Balance Sheet
- [x] Income Statement
- [x] Cash Flow
- [ ] Accounts Receivable Aging
- [ ] Accounts Payable Aging
- [ ] Inventory Valuation
- [ ] Profit & Loss by Customer
- [ ] Profit & Loss by Product

### Formulários IRS
- [x] Form 5472
- [x] Form 1099-NEC
- [x] Form 1120
- [x] Form 1040
- [ ] Form 941
- [ ] Form W-2
- [ ] Form W-3
- [ ] Form 1099-MISC
- [ ] Form 1099-INT
- [ ] Form 1099-DIV
- [ ] Schedule C
- [ ] Schedule E
- [ ] Form 1065
- [ ] Schedule K-1

### Inteligência
- [x] **Dashboard com KPIs (CONCLUÍDO)**
- [ ] Análise de tendências
- [ ] Alertas inteligentes
- [ ] Previsão de fluxo de caixa
- [ ] Chatbot assistente

### Segurança
- [x] Autenticação OAuth
- [ ] 2FA
- [ ] Criptografia de dados
- [ ] Audit log
- [ ] Permissões granulares

