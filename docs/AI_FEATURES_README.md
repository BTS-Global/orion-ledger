# 🤖 AI Features - Orion Ledger

## Overview

Orion Ledger now includes advanced AI capabilities powered by **RAG (Retrieval-Augmented Generation)**, **Active Learning**, and **Feedback Loops**. These features dramatically improve transaction classification accuracy and reduce manual data entry.

---

## 🎯 Key Features

### 1. RAG-Powered Classification
- **Semantic Search**: Find similar transactions using vector embeddings
- **Contextual Learning**: LLM receives historical context for better classification
- **Vendor Normalization**: Automatically normalize vendor names
- **Pattern Recognition**: Identify recurring transactions

### 2. Active Learning
- **Low-Confidence Detection**: Identify transactions needing human review
- **Priority Queue**: Focus on transactions with highest impact
- **Confidence Scoring**: Every prediction includes a confidence score (0-1)

### 3. Feedback Loop
- **User Corrections**: Record when users fix AI predictions
- **Continuous Improvement**: System learns from corrections
- **Performance Tracking**: Monitor accuracy trends over time
- **Automatic Retraining Suggestions**: Get notified when retraining could help

---

## 📊 Performance Metrics

### Before AI Enhancements
- Accuracy: ~70%
- Manual Review Required: 40%
- Processing Time: 5s/document

### After AI Enhancements (Target)
- Accuracy: **>90%**
- Manual Review Required: **<15%**
- Processing Time: **<3s/document**

---

## 🚀 API Endpoints

### 1. Classify Transaction with RAG

```bash
POST /api/companies/{company_id}/ai/classify/
Content-Type: application/json

{
  "description": "Coffee at Starbucks",
  "amount": 5.50,
  "vendor": "Starbucks",
  "max_examples": 5
}
```

**Response:**
```json
{
  "transaction": {
    "description": "Coffee at Starbucks",
    "amount": 5.50,
    "vendor": "Starbucks"
  },
  "suggestion": {
    "account_code": "5320",
    "account_name": "Travel and Entertainment",
    "confidence": 0.92,
    "source": "RAG"
  },
  "similar_transactions": [
    {
      "id": "uuid",
      "description": "Starbucks purchase",
      "amount": 4.75,
      "account_code": "5320",
      "similarity": 0.92
    }
  ]
}
```

### 2. Find Similar Transactions

```bash
GET /api/companies/{company_id}/ai/similar/?description=Coffee&amount=5.50&top_k=5
```

**Response:**
```json
{
  "query": {
    "description": "Coffee",
    "amount": 5.50
  },
  "similar_transactions": [
    {
      "id": "uuid",
      "description": "Coffee shop",
      "amount": 5.25,
      "account_code": "5320",
      "account_name": "Travel and Entertainment",
      "similarity": 0.89
    }
  ],
  "count": 5
}
```

### 3. Record Feedback

```bash
POST /api/companies/{company_id}/ai/feedback/
Content-Type: application/json

{
  "transaction_id": "uuid",
  "predicted_account_id": "uuid",
  "corrected_account_id": "uuid",
  "predicted_confidence": 0.75,
  "reason": "Should be office supplies, not travel"
}
```

**Response:**
```json
{
  "success": true,
  "feedback_id": "uuid",
  "feedback_type": "CORRECTION",
  "message": "Feedback recorded successfully"
}
```

### 4. Get Low-Confidence Transactions

```bash
GET /api/companies/{company_id}/ai/low-confidence/?limit=20
```

**Response:**
```json
{
  "count": 12,
  "transactions": [
    {
      "id": "uuid",
      "description": "Unknown vendor",
      "amount": 125.00,
      "suggested_account": {
        "code": "5999",
        "name": "Miscellaneous Expense"
      },
      "confidence": 0.45,
      "priority": "high"
    }
  ]
}
```

### 5. Get Accuracy Metrics

```bash
GET /api/companies/{company_id}/ai/metrics/?days=30
```

**Response:**
```json
{
  "trend": [
    {
      "date": "2025-11-01",
      "accuracy": 87.5,
      "total_predictions": 120,
      "avg_confidence": 0.82
    }
  ],
  "summary": {
    "total_feedbacks": 450,
    "corrections": 85,
    "confirmations": 365,
    "correction_rate": 18.9,
    "current_accuracy": 89.2
  },
  "retraining_recommendation": {
    "should_retrain": false,
    "reasons": []
  }
}
```

### 6. Generate Embeddings (Batch)

```bash
POST /api/companies/{company_id}/ai/generate-embeddings/
Content-Type: application/json

{
  "limit": 100
}
```

**Response:**
```json
{
  "success": true,
  "embeddings_generated": 87,
  "message": "Generated 87 embeddings"
}
```

### 7. Get RAG Statistics

```bash
GET /api/companies/{company_id}/ai/rag-stats/
```

**Response:**
```json
{
  "model_loaded": true,
  "embedding_dimension": 384,
  "total_transactions": 1250,
  "transactions_with_embeddings": 1100,
  "coverage": 88.0
}
```

---

## 🛠️ Setup & Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `sentence-transformers==2.3.1` - For embeddings
- `chromadb==0.4.22` - Vector database
- `langchain==0.1.20` - LLM orchestration
- `scikit-learn==1.4.0` - ML utilities

### 2. Run Migrations

```bash
python manage.py migrate
```

This creates:
- `Transaction.vendor`, `Transaction.category`, `Transaction.embedding` fields
- `FeedbackEntry` model for storing corrections
- `PredictionMetrics` model for tracking performance

### 3. Generate Initial Embeddings

```bash
# Via API
curl -X POST http://localhost:8000/api/companies/{company_id}/ai/generate-embeddings/ \
  -H "Content-Type: application/json" \
  -d '{"limit": 1000}'

# Or via Django shell
python manage.py shell
>>> from core.rag_service import rag_service
>>> rag_service.batch_generate_embeddings('company-uuid', limit=1000)
```

---

## 📈 How It Works

### 1. Document Processing Pipeline

```
Upload Document
    ↓
Extract Text (OCR/PDF)
    ↓
LLM Extracts Transactions
    ↓
Generate Embeddings
    ↓
RAG Finds Similar Transactions
    ↓
Enhanced Classification with Context
    ↓
Store with Confidence Score
    ↓
User Reviews & Provides Feedback
    ↓
System Learns & Improves
```

### 2. RAG Process

```python
# 1. User uploads document
document = process_document("bank_statement.pdf")

# 2. Extract transactions
transactions = extract_transactions_with_rag(text, company_id)

# 3. For each transaction:
#    a. Generate embedding
embedding = rag_service.generate_transaction_embedding({
    'description': 'Coffee at Starbucks',
    'amount': 5.50
})

#    b. Find similar transactions
similar = rag_service.find_similar_transactions(
    embedding, 
    company_id, 
    top_k=5
)

#    c. Use most similar for classification
if similar:
    suggested_account = similar[0]['account_code']
    confidence = similar[0]['similarity']
```

### 3. Feedback Loop

```python
# User corrects prediction
FeedbackService.record_correction(
    transaction_id='uuid',
    predicted_account_id='5999',
    corrected_account_id='5320',
    predicted_confidence=0.65,
    user=request.user,
    reason='Should be Travel & Entertainment'
)

# System:
# 1. Updates transaction
# 2. Regenerates embedding with correct data
# 3. Updates metrics
# 4. Learns from correction
```

---

## 🧪 Testing

### Test RAG Classification

```python
from core.rag_service import rag_service

# Generate embedding
transaction_data = {
    'description': 'AWS Cloud Services',
    'amount': 125.00,
    'vendor': 'Amazon Web Services'
}

embedding = rag_service.generate_transaction_embedding(transaction_data)

# Find similar
similar = rag_service.find_similar_transactions(
    embedding, 
    company_id='your-company-id',
    top_k=3
)

print(similar)
```

### Test Feedback Recording

```python
from core.feedback_service import FeedbackService

feedback = FeedbackService.record_correction(
    transaction_id='transaction-uuid',
    predicted_account_id='5999',
    corrected_account_id='5330',
    predicted_confidence=0.55,
    user=request.user,
    reason='Software expense, not miscellaneous'
)

print(f"Feedback type: {feedback.feedback_type}")
```

---

## 📊 Monitoring & Observability

### Check System Health

```bash
GET /api/companies/{company_id}/ai/rag-stats/
```

Monitor:
- Embedding coverage (target: >85%)
- Model load status
- Total transactions indexed

### Track Accuracy Trends

```bash
GET /api/companies/{company_id}/ai/metrics/?days=30
```

Watch for:
- Accuracy declining (may need retraining)
- High correction rate (review patterns)
- Low confidence transactions (prioritize for review)

---

## 🎓 Best Practices

### 1. Build Your Knowledge Base

- ✅ Classify at least 200-500 transactions manually first
- ✅ Ensure variety across categories
- ✅ Generate embeddings after classification

### 2. Review Low-Confidence Transactions

- ✅ Check `/ai/low-confidence/` daily
- ✅ Prioritize high-impact transactions
- ✅ Provide clear correction reasons

### 3. Monitor Performance

- ✅ Review metrics weekly
- ✅ Act on retraining recommendations
- ✅ Track accuracy trends

### 4. Optimize Embeddings

- ✅ Regenerate embeddings after bulk corrections
- ✅ Maintain >85% coverage
- ✅ Use batch generation for performance

---

## 🔮 Future Enhancements

### Phase 3 (Planned)
- [ ] Fine-tuned models per company
- [ ] Predictive analytics (cash flow, revenue)
- [ ] Anomaly detection (fraud, errors)
- [ ] Multi-language support
- [ ] Custom embedding models

### Phase 4 (Planned)
- [ ] Chatbot for financial Q&A
- [ ] Automated report narration
- [ ] Smart recommendations
- [ ] Integration with accounting rules engine

---

## 🐛 Troubleshooting

### Embeddings Not Generating

```python
# Check if model is loaded
from core.rag_service import rag_service
stats = rag_service.get_service_stats()
print(stats['model_loaded'])

# If False, restart server to initialize model
```

### Low Accuracy

1. Check embedding coverage (target: >85%)
2. Review feedback data for patterns
3. Ensure sufficient training data (500+ transactions)
4. Consider generating new embeddings

### Slow Performance

1. Check embedding cache hit rate
2. Batch generate embeddings offline
3. Limit `top_k` in similarity search
4. Consider vector database optimization

---

## 📚 References

- [RAG Architecture](../docs/AI_ENHANCEMENT_ANALYSIS.md)
- [Sentence Transformers](https://www.sbert.net/)
- [LangChain Documentation](https://python.langchain.com/)
- [Active Learning Guide](https://en.wikipedia.org/wiki/Active_learning_(machine_learning))

---

## 💡 Need Help?

- Check the [AI Enhancement Analysis](../docs/AI_ENHANCEMENT_ANALYSIS.md)
- Review [API Documentation](http://localhost:8000/api/docs/)
- See examples in `backend/core/tests/test_rag_service.py`
