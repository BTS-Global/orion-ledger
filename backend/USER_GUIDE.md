# Guia do Usuário - Accounting Software

## 📖 Bem-vindo!

Este guia irá ajudá-lo a usar todas as funcionalidades do sistema de contabilidade para empresas americanas.

## 🚀 Primeiros Passos

### 1. Acessar o Sistema

Acesse o sistema através do link fornecido:
```
https://3000-i3frgoykifkd00heetwub-abd2a201.manusvm.computer
```

### 2. Fazer Login

Na tela inicial, você verá duas opções de login:

**Opção 1: Login com Google**
- Clique em "Continue with Google"
- Selecione sua conta Google
- Autorize o acesso

**Opção 2: Login com Microsoft**
- Clique em "Continue with Microsoft"
- Entre com sua conta Microsoft
- Autorize o acesso

> **Nota**: Na primeira vez, você precisará autorizar o aplicativo a acessar suas informações básicas de perfil.

### 3. Dashboard Inicial

Após o login, você verá o Dashboard com:
- **Resumo de atividades recentes**
- **Atalhos rápidos** para principais funcionalidades
- **Menu de navegação lateral** para acessar todas as seções

## 📂 Gerenciamento de Empresas

### Cadastrar Nova Empresa

1. Acesse o **Django Admin** em `http://localhost:8000/admin`
2. Faça login com credenciais de administrador
3. Vá em **Companies** > **Add Company**
4. Preencha os dados:
   - **Company Name**: Nome da empresa
   - **Tax ID**: EIN (Employer Identification Number)
   - **Fiscal Year End**: Data de encerramento do ano fiscal (ex: 12-31)
   - **Entity Type**: Tipo de entidade (LLC, S-Corp, C-Corp, etc.)
   - **Address**: Endereço completo
5. Clique em **Save**

### Configurar Plano de Contas

1. No Admin, vá em **Chart of Accounts** > **Add**
2. Selecione a **Company**
3. Preencha:
   - **Account Code**: Código da conta (ex: 1000)
   - **Account Name**: Nome da conta (ex: Cash)
   - **Account Type**: Tipo (ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE)
   - **Parent Account**: Conta pai (opcional, para subcontas)
4. Clique em **Save**

> **Dica**: Configure o plano de contas básico antes de começar a processar transações.

## 📄 Upload e Processamento de Documentos

### Como Fazer Upload

1. No menu lateral, clique em **Documents**
2. Você verá a área de upload com drag-and-drop
3. **Opção 1**: Arraste arquivos para a área marcada
4. **Opção 2**: Clique na área e selecione arquivos

**Formatos Aceitos**:
- PDF (extratos bancários)
- CSV (arquivos de transações)
- PNG/JPG (imagens de documentos)

### Acompanhar Processamento

Após o upload, o sistema:
1. **Salva o documento** no banco de dados
2. **Inicia processamento assíncrono** (1-2 minutos)
3. **Extrai dados** usando OCR e IA
4. **Atualiza status** para PROCESSED

Você verá o status atualizado na lista de documentos:
- 🟡 **PENDING**: Aguardando processamento
- 🟡 **PROCESSING**: Em processamento
- 🟢 **PROCESSED**: Concluído com sucesso
- 🔴 **FAILED**: Erro no processamento

### Visualizar Documentos

Na lista de documentos, você pode:
- Ver **nome do arquivo**
- Ver **tipo e data de upload**
- Verificar **status do processamento**
- Clicar em **View Details** para mais informações

## 💰 Validação de Transações

### Acessar Transações Extraídas

1. No menu lateral, clique em **Transactions**
2. Você verá todas as transações extraídas dos documentos
3. Transações aparecem com status **PENDING** (aguardando validação)

### Validar Transação

Para cada transação, você pode:

1. **Revisar os dados extraídos**:
   - Data
   - Descrição
   - Valor
   - Categoria sugerida

2. **Editar se necessário**:
   - Clique no ícone de edição
   - Corrija informações incorretas
   - Ajuste a categoria

3. **Aprovar a transação**:
   - Clique em **Approve**
   - A transação será marcada como APPROVED
   - Lançamentos contábeis serão criados automaticamente

### Categorias de Transações

O sistema categoriza automaticamente em:
- **REVENUE**: Receitas
- **EXPENSE**: Despesas
- **ASSET**: Ativos
- **LIABILITY**: Passivos
- **EQUITY**: Patrimônio líquido

> **Importante**: Revise sempre as categorias sugeridas para garantir precisão contábil.

## 📊 Relatórios Financeiros

### Gerar Relatórios

1. No menu lateral, clique em **Reports**
2. Selecione o tipo de relatório:
   - **Balance Sheet** (Balanço Patrimonial)
   - **Income Statement** (DRE)
   - **Cash Flow** (Fluxo de Caixa)

### Balance Sheet (Balanço Patrimonial)

**O que mostra**: Posição financeira em uma data específica

**Como gerar**:
1. Selecione a aba **Balance Sheet**
2. Escolha a **data de referência**
3. Clique em **Generate Report**

**Informações exibidas**:
- **Assets** (Ativos): Current Assets, Fixed Assets
- **Liabilities** (Passivos): Current Liabilities, Long-term Liabilities
- **Equity** (Patrimônio Líquido): Capital, Retained Earnings
- **Validação**: Total Assets = Total Liabilities + Equity

### Income Statement (DRE)

**O que mostra**: Receitas e despesas em um período

**Como gerar**:
1. Selecione a aba **Income Statement**
2. Escolha **data inicial** e **data final**
3. Clique em **Generate Report**

**Informações exibidas**:
- **Revenues** (Receitas): Por categoria
- **Expenses** (Despesas): Por categoria
- **Net Income** (Lucro Líquido): Receitas - Despesas

### Cash Flow Statement (Fluxo de Caixa)

**O que mostra**: Entradas e saídas de caixa

**Como gerar**:
1. Selecione a aba **Cash Flow**
2. Escolha o **período**
3. Clique em **Generate Report**

**Informações exibidas**:
- **Operating Activities**: Atividades operacionais
- **Investing Activities**: Investimentos
- **Financing Activities**: Financiamentos
- **Net Change in Cash**: Variação líquida

### Exportar Relatórios

Após gerar o relatório, você pode:
- **Exportar para Excel**: Clique em "Export to Excel"
- **Exportar para PDF**: Clique em "Export to PDF"

Os arquivos serão baixados automaticamente.

## 📝 Formulários IRS

### Tipos de Formulários Disponíveis

O sistema gera automaticamente 4 tipos de formulários:

1. **Form 5472** - Information Return
   - Para empresas com 25%+ propriedade estrangeira
   - Reporta transações com partes relacionadas

2. **Form 1099-NEC** - Nonemployee Compensation
   - Para pagamentos a contratados independentes
   - Valor mínimo: $600

3. **Form 1120** - Corporate Income Tax Return
   - Declaração de imposto de renda corporativo
   - Para C-Corporations

4. **Form 1040** - Individual Income Tax Return
   - Declaração de imposto de renda individual
   - Para proprietários/sócios

### Gerar Formulário

1. No menu lateral, clique em **IRS Forms**
2. Na seção "Generate New Form":
   - Selecione o **tipo de formulário**
   - Escolha o **ano fiscal**
3. Clique em **Generate Form**

O sistema irá:
- Buscar dados contábeis automaticamente
- Mapear para os campos do formulário
- Gerar PDF do formulário
- Salvar com status DRAFT

### Revisar Formulário

1. Na lista "Generated Forms", encontre o formulário
2. Verifique as informações:
   - Tipo de formulário
   - Ano fiscal
   - Status
   - Data de criação
3. Clique em **Download PDF** para revisar

### Baixar PDF

1. Clique no botão **Download PDF**
2. O arquivo será baixado automaticamente
3. Abra e revise cuidadosamente

> **⚠️ IMPORTANTE**: Os PDFs gerados são representações simplificadas. Sempre consulte um contador antes de enviar ao IRS.

### Marcar como Enviado

Após enviar o formulário ao IRS:
1. Encontre o formulário na lista
2. Clique em **Mark as Filed** (disponível via API)
3. O status mudará para FILED

## 🔐 Segurança e Privacidade

### Autenticação

- Login federado seguro (OAuth 2.0)
- Sessões criptografadas
- Logout automático após inatividade

### Dados

- Todos os dados são armazenados de forma segura
- Backup automático
- Trilha de auditoria completa

### Permissões

- Acesso baseado em usuário
- Cada usuário vê apenas suas empresas
- Administradores têm acesso total

## 🆘 Solução de Problemas

### Upload Falhou

**Problema**: Documento não foi processado

**Soluções**:
1. Verifique o formato do arquivo (PDF, CSV, PNG, JPG)
2. Verifique o tamanho (máximo 10MB)
3. Tente fazer upload novamente
4. Se persistir, entre em contato com suporte

### Transação Não Aparece

**Problema**: Transação extraída não aparece na lista

**Soluções**:
1. Aguarde 1-2 minutos (processamento assíncrono)
2. Atualize a página
3. Verifique se o documento foi processado com sucesso
4. Verifique o status do documento (deve estar PROCESSED)

### Relatório Vazio

**Problema**: Relatório não mostra dados

**Soluções**:
1. Verifique se há transações aprovadas no período
2. Confirme as datas selecionadas
3. Verifique se as transações foram categorizadas corretamente

### Formulário IRS Incorreto

**Problema**: Dados no formulário estão incorretos

**Soluções**:
1. Revise as transações e categorias
2. Corrija dados contábeis
3. Gere o formulário novamente
4. Sempre consulte um contador profissional

## 💡 Dicas e Melhores Práticas

### Organização

1. **Configure o plano de contas** antes de processar transações
2. **Categorize transações** assim que forem extraídas
3. **Revise relatórios mensalmente** para detectar erros
4. **Faça backup** dos PDFs gerados

### Eficiência

1. **Use drag-and-drop** para upload rápido de múltiplos arquivos
2. **Aprove transações em lote** quando possível
3. **Exporte relatórios regularmente** para análise externa
4. **Gere formulários IRS** com antecedência

### Precisão

1. **Sempre revise dados extraídos** antes de aprovar
2. **Valide categorias** de transações
3. **Confira relatórios** antes de exportar
4. **Consulte contador** antes de enviar formulários ao IRS

## 📞 Suporte

### Documentação Adicional

- **README.md**: Documentação técnica completa
- **API Docs**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/

### Contato

Para suporte técnico ou dúvidas:
- Email: support@example.com
- Documentação: Consulte README_COMPLETO.md

## 🎓 Glossário

**EIN**: Employer Identification Number - Número de identificação fiscal da empresa

**OCR**: Optical Character Recognition - Reconhecimento óptico de caracteres

**DRE**: Demonstração do Resultado do Exercício (Income Statement)

**Dupla Entrada**: Sistema contábil onde cada transação afeta pelo menos duas contas

**Ano Fiscal**: Período de 12 meses usado para fins contábeis e fiscais

**Form 5472**: Formulário IRS para empresas com propriedade estrangeira

**Form 1099-NEC**: Formulário IRS para reportar pagamentos a contratados

**Form 1120**: Formulário IRS de declaração de imposto corporativo

**Form 1040**: Formulário IRS de declaração de imposto individual

---

**Última atualização**: 2025-10-18
**Versão**: 1.0.0

