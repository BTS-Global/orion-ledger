# Roadmap Revisado v1.0: Orion Universal Ledger

**Foco:** EUA + Jurisdições Offshore (Caribe)  
**Brasil:** Movido para v2.0  
**Data:** 22 de Outubro de 2025  
**Autor:** Manus AI

---

## 1. Decisão Estratégica

Após análise, decidimos **focar a v1.0** em:
- ✅ **Estados Unidos** (já implementado, expandir)
- ✅ **Jurisdições Offshore** (Caribe: BVI, Cayman, Seychelles, etc.)
- ✅ **Cross-border entre EUA e Offshore**
- ✅ **Compliance Internacional** (FATCA/CRS)
- ✅ **Transfer Pricing** (básico)

**Brasil será implementado na v2.0**, pois:
- Não é essencial para o core business inicial (offshore + EUA)
- SPED é complexo e específico (requer tempo dedicado)
- Permite lançamento mais rápido da v1.0

---

## 2. Roadmap v1.0 Revisado

### Fase 1: Fundação Multi-Jurisdição (1.5-2 meses)
**Objetivo:** Preparar o sistema para suportar múltiplas jurisdições e moedas.

**Entregáveis:**
- [x] Análise dos repositórios existentes ✅
- [x] Pesquisa de requisitos de compliance ✅
- [x] Plano de unificação e arquitetura ✅
- [ ] Refatorar modelos de dados para multi-jurisdição
  - Adicionar campo `jurisdiction` a `Company`
  - Adicionar campo `currency` a `ChartOfAccounts` e `Transaction`
  - Criar modelo `Jurisdiction` (configurações por jurisdição)
- [ ] Implementar motor de conversão de moedas
  - Integração com API de câmbio (Open Exchange Rates ou similar)
  - Modelo `ExchangeRate` para histórico
  - Função `convert_currency(amount, from_currency, to_currency, date)`
- [ ] Migrar lógica dos EUA para módulo plugável
  - Criar app `jurisdiction_us`
  - Mover código de formulários IRS para o módulo
  - Abstrair lógica de relatórios para ser agnóstica

**Tecnologias:**
- Django migrations para refatoração de modelos
- API de câmbio: Open Exchange Rates (free tier: 1000 requests/mês)
- Celery task para atualização diária de taxas

---

### Fase 2: Módulo Offshore (Caribe) (1.5-2 meses)
**Objetivo:** Adicionar suporte completo para jurisdições offshore populares.

**Entregáveis:**
- [ ] Criar app `jurisdiction_caribbean`
- [ ] Implementar geração de **Annual Return** (BVI)
  - Modelo `AnnualReturn`
  - Mapeamento de contas para campos do Annual Return
  - Geração de PDF preenchido
  - Status tracking (DRAFT, READY, SUBMITTED)
- [ ] Implementar **Economic Substance Reporting**
  - Modelo `EconomicSubstanceReport`
  - Formulário para documentar substância (funcionários, despesas, ativos)
  - Geração de relatório PDF
- [ ] Implementar tracking de **taxas anuais**
  - Modelo `AnnualFee` (jurisdição, valor, data de vencimento)
  - Alertas automáticos para prazos
  - Dashboard de compliance com status
- [ ] Adicionar suporte para outras jurisdições
  - Cayman Islands
  - Seychelles
  - Marshall Islands
  - Belize

**Tecnologias:**
- PyPDFForm para preenchimento de PDFs
- Celery beat para alertas automáticos
- Django signals para notificações

---

### Fase 3: Expansão de Formulários IRS (Cross-border) (1 mês)
**Objetivo:** Adicionar formulários IRS essenciais para operações cross-border.

**Entregáveis:**
- [ ] Implementar **Form 8938** (Statement of Specified Foreign Financial Assets)
  - Para US Persons com ativos estrangeiros > $50k
  - Mapeamento de contas offshore
  - Geração de PDF
- [ ] Implementar **FBAR / FinCEN Form 114**
  - Para US Persons com contas estrangeiras > $10k
  - Integração com dados de contas offshore
  - Geração de arquivo XML (submissão eletrônica)
- [ ] Implementar **Form 5471** (Information Return - Foreign Corporations)
  - Para US Persons com participação em empresas estrangeiras
  - Mapeamento de dados financeiros da empresa offshore
  - Geração de PDF
- [ ] Melhorar formulários existentes
  - Form 5472 (já implementado, melhorar)
  - Form 1120 (adicionar Schedule C para foreign income)

**Tecnologias:**
- PyPDFForm para PDFs
- lxml para geração de XML (FBAR)

---

### Fase 4: Compliance Internacional (FATCA/CRS) (1.5 meses)
**Objetivo:** Automatizar identificação e reporte de contas para FATCA/CRS.

**Entregáveis:**
- [ ] Criar app `compliance_intl`
- [ ] Implementar **motor de identificação de contas reportáveis**
  - Modelo `ReportableAccount`
  - Regras FATCA (US Persons)
  - Regras CRS (residentes fiscais de países participantes)
  - Interface para self-certification de clientes
- [ ] Implementar geração de **relatórios FATCA**
  - Form 8938 (já na Fase 3)
  - FBAR (já na Fase 3)
  - Relatório consolidado de ativos estrangeiros
- [ ] Implementar geração de **relatórios CRS**
  - Formato XML conforme OECD CRS XML Schema
  - Relatórios por jurisdição
- [ ] Dashboard de compliance
  - Lista de contas reportáveis
  - Status de due diligence
  - Alertas para prazos

**Tecnologias:**
- lxml para geração de XML CRS
- Django admin customizado para due diligence

---

### Fase 5: Transfer Pricing (Básico) (1.5 meses)
**Objetivo:** Fornecer ferramentas básicas para documentação de transfer pricing.

**Entregáveis:**
- [ ] Criar app `transfer_pricing`
- [ ] Implementar **documentação de transações intercompany**
  - Modelo `TransferPricingTransaction`
  - Interface para registrar transações entre partes relacionadas
  - Classificação por tipo (bens, serviços, intangíveis, financiamento)
- [ ] Implementar **métodos de TP básicos**
  - CUP (Comparable Uncontrolled Price)
  - RPM (Resale Price Method)
  - CPM (Cost Plus Method)
  - Cálculo de arm's length range
- [ ] Implementar geração de **documentação básica**
  - Transfer Pricing Policy (documento de políticas)
  - Transaction Summary (resumo de transações)
  - **Nota:** Master File, Local File e CbCR ficam para v2.0
- [ ] Dashboard de TP
  - Lista de transações intercompany
  - Análise de conformidade com arm's length
  - Alertas para transações fora do range

**Tecnologias:**
- WeasyPrint para geração de documentos PDF
- Pandas para análise de dados

---

### Fase 6: Relatórios Consolidados e Lançamento (1 mês)
**Objetivo:** Unificar visão financeira e preparar para lançamento.

**Entregáveis:**
- [ ] Implementar **consolidação de demonstrações financeiras**
  - Conversão de balanços de diferentes moedas para moeda base
  - Eliminação de transações intercompany
  - Balance Sheet consolidado
  - Income Statement consolidado
  - Cash Flow consolidado
- [ ] Implementar **dashboards de BI**
  - Dashboard global com visão de todas as entidades
  - Análise de carga tributária efetiva por jurisdição
  - Relatórios de exposição cambial
  - Gráficos interativos (recharts)
- [ ] Testes de integração completos
  - Testes end-to-end de fluxos principais
  - Testes de performance
  - Testes de segurança
- [ ] Documentação final
  - Manual do usuário atualizado
  - Documentação de API (Swagger)
  - Guia de deployment
- [ ] Deploy em produção
  - Configuração de infraestrutura (Kubernetes)
  - CI/CD pipeline
  - Monitoramento (Sentry, Prometheus)

**Tecnologias:**
- Playwright para testes E2E
- Swagger/OpenAPI para documentação de API
- Kubernetes + Docker para deployment

---

## 3. Cronograma v1.0

| Fase | Duração | Início | Fim |
|------|---------|--------|-----|
| Fase 1: Fundação Multi-Jurisdição | 1.5-2 meses | Mês 1 | Mês 2 |
| Fase 2: Módulo Offshore (Caribe) | 1.5-2 meses | Mês 2.5 | Mês 4 |
| Fase 3: Expansão IRS (Cross-border) | 1 mês | Mês 4.5 | Mês 5.5 |
| Fase 4: Compliance Internacional | 1.5 meses | Mês 5.5 | Mês 7 |
| Fase 5: Transfer Pricing (Básico) | 1.5 meses | Mês 7 | Mês 8.5 |
| Fase 6: Consolidação e Lançamento | 1 mês | Mês 8.5 | Mês 9.5 |
| **TOTAL v1.0** | **8.5-9.5 meses** | - | - |

**Redução de 14-16 meses para 8.5-9.5 meses (~40% mais rápido)** 🚀

---

## 4. Roadmap v2.0 (Futuro)

### Módulo Brasil (3-4 meses)
- SPED Contábil (ECD)
- SPED Fiscal (ECF)
- e-Financeira
- Apuração de IRPJ/CSLL
- Geração de DARFs

### Transfer Pricing Avançado (1.5 meses)
- Análise de comparáveis (benchmarking)
- Base de dados de comparáveis
- Geração de Master File
- Geração de Local File
- Geração de Country-by-Country Report (CbCR)

### Outras Jurisdições
- União Europeia (VAT, Corporate Tax)
- Ásia (Hong Kong, Singapore)
- América Latina (Panamá, Uruguai)

---

## 5. Funcionalidades v1.0 (Resumo)

### Core
- ✅ Gestão multi-empresa (já implementado)
- ✅ Contabilidade de dupla entrada (já implementado)
- ✅ Upload e processamento de documentos (já implementado)
- ✅ Extração inteligente com OpenAI (já implementado)
- ✅ Relatórios financeiros (já implementado)
- 🆕 Multi-moeda com conversão automática
- 🆕 Multi-jurisdição (EUA + Offshore)

### EUA (Expandido)
- ✅ Form 5472 (já implementado)
- ✅ Form 1099-NEC (já implementado)
- ✅ Form 1120 (já implementado)
- ✅ Form 1040 (já implementado)
- 🆕 Form 8938 (ativos estrangeiros)
- 🆕 FBAR (contas estrangeiras)
- 🆕 Form 5471 (empresas estrangeiras)

### Offshore (Novo)
- 🆕 Annual Return (BVI, Cayman, Seychelles, etc.)
- 🆕 Economic Substance Reporting
- 🆕 Tracking de taxas anuais
- 🆕 Dashboard de compliance

### Cross-border (Novo)
- 🆕 Conversão de moedas
- 🆕 Relatórios consolidados multi-jurisdição
- 🆕 Eliminação de transações intercompany
- 🆕 FATCA/CRS compliance
- 🆕 Transfer Pricing (básico)

---

## 6. Diferenciais Competitivos v1.0

1. **Único software focado em EUA + Offshore integrado**
   - Não é necessário usar sistemas separados

2. **Compliance automatizado**
   - Geração automática de formulários IRS
   - Annual Returns para jurisdições offshore
   - FATCA/CRS compliance

3. **Multi-moeda nativo**
   - Conversão automática de moedas
   - Relatórios consolidados

4. **Transfer Pricing integrado**
   - Documentação de transações intercompany
   - Análise de conformidade

5. **Arquitetura modular**
   - Fácil adição de novas jurisdições (v2.0)

---

## 7. Próximos Passos Imediatos

### 1. Aprovação do Roadmap Revisado
- [ ] Revisar e aprovar este roadmap
- [ ] Confirmar prioridades
- [ ] Alocar recursos

### 2. Início da Fase 1 (Esta Semana)
- [ ] Criar branch `feature/multi-jurisdiction`
- [ ] Refatorar modelos de dados
- [ ] Implementar motor de conversão de moedas
- [ ] Testes unitários

### 3. Setup de Infraestrutura
- [ ] Configurar API de câmbio (Open Exchange Rates)
- [ ] Configurar Celery beat para atualização de taxas
- [ ] Configurar ambiente de staging

---

## 8. Métricas de Sucesso v1.0

### Técnicas
- [ ] Suporte para pelo menos 5 jurisdições offshore (BVI, Cayman, Seychelles, Marshall Islands, Belize)
- [ ] Conversão de moedas com latência < 100ms
- [ ] Geração de relatórios consolidados em < 5 segundos
- [ ] Cobertura de testes > 80%

### Negócio
- [ ] Onboarding de pelo menos 10 empresas beta
- [ ] Geração de 100+ formulários IRS
- [ ] Geração de 50+ Annual Returns
- [ ] NPS > 8.0

### Compliance
- [ ] 100% de conformidade com requisitos FATCA
- [ ] 100% de conformidade com requisitos CRS
- [ ] 100% de conformidade com requisitos de Annual Return (BVI)

---

## 9. Conclusão

O roadmap revisado para v1.0 foca no **core business essencial**: operações entre **EUA e jurisdições offshore**. Isso permite:

- ✅ **Lançamento mais rápido** (8.5-9.5 meses vs. 14-16 meses)
- ✅ **Foco no mercado principal** (offshore + EUA)
- ✅ **Validação de mercado** antes de expandir para Brasil
- ✅ **Arquitetura preparada** para v2.0 (Brasil e outras jurisdições)

**Brasil na v2.0** é uma decisão estratégica que permite:
- Dedicar tempo adequado para complexidade do SPED
- Validar produto com mercado offshore primeiro
- Adicionar Brasil com qualidade após feedback de v1.0

**Pronto para começar a Fase 1!** 🚀

