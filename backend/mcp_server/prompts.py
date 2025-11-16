"""
MCP Prompts
Reusable prompt templates for accounting tasks
"""
from typing import Dict, Any, Optional
from string import Template


class PromptTemplate:
    """Base class for prompt templates"""
    
    def __init__(self, template: str):
        self.template = Template(template)
    
    def render(self, **kwargs) -> str:
        """Render template with variables"""
        return self.template.safe_substitute(**kwargs)


# Monthly Financial Analysis Prompt
MONTHLY_ANALYSIS_PROMPT = PromptTemplate("""
Analise o desempenho financeiro da empresa $company_name no período de $period.

## Dados Disponíveis:

### Receitas:
$revenue_data

### Despesas:
$expense_data

### Lucro Líquido: $net_income

### Total de Transações: $transaction_count

## Sua Análise Deve Incluir:

1. **Resumo Executivo**: Visão geral do desempenho no período
2. **Principais Variações**: Mudanças superiores a 10% em relação ao período anterior
3. **Tendências Identificadas**: Padrões observados nos dados
4. **Recomendações de Ação**: Sugestões concretas baseadas na análise
5. **Alertas de Atenção**: Pontos que requerem atenção especial

Formate sua resposta de forma profissional e acessível.
""")


# Batch Classification Prompt
BATCH_CLASSIFICATION_PROMPT = PromptTemplate("""
Você precisa classificar $count transações de forma consistente usando o plano de contas da empresa.

## Transações para Classificar:

$transactions

## Plano de Contas Disponível:

$chart_of_accounts

## Instruções:

1. Para cada transação, sugira a conta contábil mais adequada
2. Baseie-se em transações similares históricas quando disponíveis
3. Seja consistente na classificação de transações similares
4. Forneça uma justificativa curta para cada classificação
5. Indique o nível de confiança (0.0 a 1.0)

## Formato de Resposta:

Retorne um array JSON com este formato:

```json
[
  {
    "transaction_index": 0,
    "suggested_account": "código_da_conta",
    "account_name": "nome_da_conta",
    "confidence": 0.95,
    "reasoning": "justificativa"
  },
  ...
]
```
""")


# Accounting Assistant Prompt
ACCOUNTING_ASSISTANT_PROMPT = PromptTemplate("""
Você é um assistente contábil especializado da empresa $company_name.

## Contexto da Empresa:

- **Nome**: $company_name
- **Ramo de Atividade**: $industry
- **Porte**: $size
- **Regime Tributário**: $tax_regime
- **Período Fiscal**: $fiscal_period

## Dados Disponíveis:

- **Transações Registradas**: $transaction_count
- **Contas Ativas**: $account_count
- **Último Balancete**: $last_trial_balance_date

## Plano de Contas (Resumo):

$chart_of_accounts_summary

## Suas Responsabilidades:

1. Responder perguntas sobre contabilidade e classificações
2. Explicar relatórios financeiros de forma clara
3. Ajudar com questões de compliance e regulamentação
4. Sugerir melhorias nos processos contábeis
5. Identificar possíveis problemas ou inconsistências

## Estilo de Comunicação:

- Use linguagem profissional mas acessível
- Explique termos técnicos quando necessário
- Seja preciso e baseado em dados
- Ofereça exemplos práticos quando relevante

Como posso ajudá-lo hoje?
""")


# Transaction Classification Context Prompt
CLASSIFICATION_CONTEXT_PROMPT = PromptTemplate("""
Classifique a seguinte transação no plano de contas da empresa.

## Transação:

- **Descrição**: $description
- **Valor**: $amount
- **Data**: $date
- **Fornecedor/Cliente**: $vendor
- **Documento**: $document_number

## Transações Similares Históricas:

$similar_transactions

## Plano de Contas Relevante:

$relevant_accounts

## Instruções:

1. Analise a transação e o contexto histórico
2. Identifique a conta contábil mais apropriada
3. Considere o tipo de transação (receita, despesa, ativo, etc.)
4. Seja consistente com classificações anteriores similares

## Resposta Esperada (JSON):

```json
{
  "account_code": "código da conta",
  "account_name": "nome da conta",
  "confidence": 0.92,
  "reasoning": "Baseado em X transações similares anteriores..."
}
```
""")


# Audit Report Prompt
AUDIT_REPORT_PROMPT = PromptTemplate("""
Analise as transações do período $period e identifique possíveis problemas.

## Estatísticas do Período:

- **Total de Transações**: $transaction_count
- **Valor Total**: $total_amount
- **Contas Utilizadas**: $accounts_used
- **Fornecedores Únicos**: $unique_vendors

## Análises Realizadas:

$analysis_results

## Anomalias Encontradas:

$anomalies

## Sua Tarefa:

1. Revisar as anomalias identificadas
2. Classificar por severidade (Crítica, Alta, Média, Baixa)
3. Sugerir ações corretivas específicas
4. Identificar padrões ou tendências preocupantes
5. Recomendar melhorias nos controles internos

Formate sua resposta como um relatório de auditoria profissional.
""")


# Document Analysis Prompt
DOCUMENT_ANALYSIS_PROMPT = PromptTemplate("""
Analise o documento fornecido e extraia informações contábeis relevantes.

## Texto Extraído (OCR):

$document_text

## Informações Identificadas:

$identified_entities

## Sua Tarefa:

1. Identificar o tipo de documento (nota fiscal, recibo, boleto, etc.)
2. Extrair dados estruturados (fornecedor, data, valor, itens)
3. Sugerir classificação contábil para cada item
4. Indicar nível de confiança nas extrações

## Formato de Resposta (JSON):

```json
{
  "document_type": "invoice",
  "confidence": 0.89,
  "vendor": "nome do fornecedor",
  "invoice_number": "número da NF",
  "date": "YYYY-MM-DD",
  "total_amount": 1500.00,
  "line_items": [
    {
      "description": "descrição do item",
      "amount": 1200.00,
      "suggested_account": "código da conta",
      "confidence": 0.92
    }
  ]
}
```
""")


# Custom Report Generation Prompt
CUSTOM_REPORT_PROMPT = PromptTemplate("""
Gere um relatório financeiro personalizado baseado na solicitação do usuário.

## Solicitação do Usuário:

"$user_query"

## Dados Disponíveis:

$available_data

## Período de Análise:

$period

## Instruções:

1. Interprete a solicitação do usuário
2. Extraia e organize os dados relevantes
3. Calcule métricas e totalizações necessárias
4. Identifique insights e tendências
5. Formate de forma clara e profissional

## Formato da Resposta:

```json
{
  "report_title": "título do relatório",
  "data": [
    // dados estruturados
  ],
  "summary": "resumo executivo",
  "insights": [
    "insight 1",
    "insight 2"
  ],
  "visualizations": {
    // sugestões de gráficos
  }
}
```
""")


# Prompt Registry
PROMPT_REGISTRY = {
    "monthly_financial_analysis": MONTHLY_ANALYSIS_PROMPT,
    "batch_classification": BATCH_CLASSIFICATION_PROMPT,
    "accounting_assistant": ACCOUNTING_ASSISTANT_PROMPT,
    "classification_context": CLASSIFICATION_CONTEXT_PROMPT,
    "audit_report": AUDIT_REPORT_PROMPT,
    "document_analysis": DOCUMENT_ANALYSIS_PROMPT,
    "custom_report": CUSTOM_REPORT_PROMPT,
}


def get_prompt(prompt_name: str, **kwargs) -> str:
    """Get rendered prompt by name"""
    template = PROMPT_REGISTRY.get(prompt_name)
    
    if not template:
        raise ValueError(f"Unknown prompt: {prompt_name}")
    
    return template.render(**kwargs)


def list_prompts() -> Dict[str, str]:
    """List all available prompts"""
    return {
        name: template.template.template
        for name, template in PROMPT_REGISTRY.items()
    }
