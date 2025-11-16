# Integração com Manus LLM API

Este documento descreve a integração do Orion Ledger com a **Manus LLM API** para processamento de documentos e extração de transações.

## 📋 Sobre

O Orion Ledger usa LLMs (Large Language Models) para extrair automaticamente transações de documentos financeiros (PDFs, imagens, textos). Anteriormente, usávamos a API da OpenAI diretamente. Agora, usamos a **Manus LLM API**, que oferece:

- ✅ **Formato OpenAI-compatible** - Mesma interface da OpenAI
- ✅ **Múltiplos modelos** - gpt-4.1-mini, gpt-4.1-nano, gemini-2.5-flash
- ✅ **Custo otimizado** - Melhor controle de gastos
- ✅ **Centralização** - Todas as chamadas LLM gerenciadas pelo Manus

## 🔧 Configuração

### Variáveis de Ambiente

Configure as seguintes variáveis no arquivo `.env`:

```bash
# Manus LLM API Configuration
OPENAI_API_KEY=your-manus-api-key-here
OPENAI_BASE_URL=https://api.manus.ai/v1
```

**Nota:** Apesar do nome `OPENAI_API_KEY`, esta variável agora contém a chave da API Manus. O nome foi mantido para compatibilidade com a biblioteca `openai`.

### Modelos Disponíveis

A Manus API oferece os seguintes modelos:

| Modelo | Descrição | Uso Recomendado |
|--------|-----------|-----------------|
| `gpt-4.1-mini` | Rápido e eficiente | **Padrão** - Extração de transações |
| `gpt-4.1-nano` | Mais econômico | Tarefas simples |
| `gemini-2.5-flash` | Alternativa Google | Testes e comparações |

## 💻 Implementação

### Código Atual

O código usa a biblioteca `openai` (versão moderna) com formato OpenAI-compatible:

```python
from openai import OpenAI

# Initialize Manus API client (OpenAI-compatible)
# API key and base URL are already configured in environment variables
client = OpenAI()

# Call Manus API
response = client.chat.completions.create(
    model="gpt-4.1-mini",  # Manus model
    messages=[
        {"role": "system", "content": "You are a financial data extraction assistant."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1,
    max_tokens=2000
)

# Parse response
result = response.choices[0].message.content
```

### Onde é Usado

A Manus API é usada em:

**`documents/tasks.py`:**
- `extract_transactions_from_text()` - Extração de transações de texto livre usando LLM

**Fluxo:**
1. Documento é carregado (PDF, imagem, CSV)
2. Texto é extraído (OCR, pdfplumber, etc.)
3. Se não houver estrutura clara, usa LLM para extrair transações
4. LLM retorna JSON com transações estruturadas
5. Transações são criadas no banco de dados

## 🔄 Migração da OpenAI para Manus

### O Que Mudou

| Antes (OpenAI) | Depois (Manus) |
|----------------|----------------|
| `import openai` (old API) | `from openai import OpenAI` (new API) |
| `openai.api_key = settings.OPENAI_API_KEY` | `client = OpenAI()` |
| `openai.ChatCompletion.create()` | `client.chat.completions.create()` |
| `model="gpt-3.5-turbo"` | `model="gpt-4.1-mini"` |

### Compatibilidade

A mudança é **100% compatível** porque:

1. A Manus API usa o **mesmo formato da OpenAI**
2. A biblioteca `openai` é a mesma
3. Apenas o modelo e a base URL mudaram
4. Variáveis de ambiente configuradas automaticamente

## 📊 Prompt de Extração

O prompt usado para extração de transações:

```
Extract all financial transactions from the following text.
For each transaction, provide:
- date (YYYY-MM-DD format)
- description
- amount (positive for income/deposits, negative for expenses/withdrawals)
- category (if identifiable)

Text:
{text[:4000]}

Return ONLY a JSON array of transactions, no other text. Example format:
[{"date": "2024-01-15", "description": "Grocery Store", "amount": -45.50, "category": "Groceries"}]
```

**Resposta Esperada:**

```json
[
  {
    "date": "2024-01-15",
    "description": "Grocery Store",
    "amount": -45.50,
    "category": "Groceries"
  },
  {
    "date": "2024-01-16",
    "description": "Salary Deposit",
    "amount": 5000.00,
    "category": "Income"
  }
]
```

## 🧪 Testes

### Testar Localmente

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "user", "content": "Extract transactions from: 01/15/2024 $45.50 Grocery Store"}
    ]
)

print(response.choices[0].message.content)
```

### Fallback

Se a API Manus falhar, o sistema usa **pattern matching** como fallback:

```python
def extract_transactions_pattern_matching(text):
    """Fallback: Extract transactions using regex patterns."""
    import re
    # Pattern for date + amount + description
    pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+\$?([\d,]+\.\d{2})\s+(.+?)(?=\n|$)'
    matches = re.findall(pattern, text, re.MULTILINE)
    # ...
```

## 📈 Benefícios

### Custo

- **Antes:** Custos diretos com OpenAI
- **Depois:** Custos gerenciados pelo Manus, melhor controle

### Centralização

- **Antes:** Chaves API espalhadas
- **Depois:** Todas as chamadas LLM via Manus

### Flexibilidade

- **Antes:** Apenas modelos OpenAI
- **Depois:** Múltiplos modelos (GPT, Gemini)

### Rastreabilidade

- **Antes:** Logs dispersos
- **Depois:** Logs centralizados no Manus

## 🔒 Segurança

- ✅ API key armazenada em variável de ambiente
- ✅ Nunca commitada no código
- ✅ `.env.example` com placeholders
- ✅ Biblioteca oficial `openai` (segura e mantida)

## 📚 Referências

- [OpenAI Python Library](https://github.com/openai/openai-python)
- [Manus API Documentation](https://docs.manus.ai)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## 🚀 Próximos Passos

1. ✅ Substituir OpenAI por Manus API
2. Testar extração de transações com diferentes tipos de documentos
3. Ajustar prompts para melhor precisão
4. Considerar usar `gpt-4.1-nano` para tarefas simples (economia)
5. Implementar cache de respostas para documentos similares
6. Adicionar métricas de uso e custo

## 📝 Changelog

### 2025-01-XX - Migração para Manus API

- ✅ Substituída API OpenAI por Manus API
- ✅ Atualizado código para usar biblioteca `openai` moderna
- ✅ Modelo alterado de `gpt-3.5-turbo` para `gpt-4.1-mini`
- ✅ Documentação atualizada
- ✅ `.env.example` atualizado com configurações Manus

---

**Desenvolvido para Orion Ledger - BTS Global Corp**
