"""
RAG (Retrieval-Augmented Generation) Service for Orion Ledger.

This service provides:
- Vector embeddings for transactions
- Semantic search for similar transactions
- Context retrieval for LLM prompts
- Knowledge base management
"""
import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
import numpy as np

# Conditional import for sentence-transformers (may not be available in test environment)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for transaction classification and retrieval."""
    
    # Singleton instance
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize RAG service with embedding model."""
        if self._initialized:
            return
            
        logger.info("Initializing RAG Service...")
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("sentence-transformers not available. RAG Service will run in limited mode.")
            self._model = None
            self._embedding_dim = 384
            self._initialized = True
            return
        
        try:
            # Load lightweight embedding model
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
            self._embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
            logger.info("RAG Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            self._model = None
        
        self._initialized = True
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        if not self._model:
            logger.warning("Embedding model not available")
            return None
        
        # Check cache first
        cache_key = f"embedding:{hash(text)}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # Generate embedding
            embedding = self._model.encode(text, convert_to_numpy=True)
            embedding_list = embedding.tolist()
            
            # Cache for 1 hour
            cache.set(cache_key, embedding_list, 3600)
            
            return embedding_list
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def generate_transaction_embedding(self, transaction_data: Dict) -> Optional[List[float]]:
        """
        Generate embedding for a transaction.
        
        Args:
            transaction_data: Dictionary with transaction fields
            
        Returns:
            Embedding vector
        """
        # Create rich text representation
        text_parts = []
        
        if 'description' in transaction_data:
            text_parts.append(f"Description: {transaction_data['description']}")
        
        if 'vendor' in transaction_data and transaction_data['vendor']:
            text_parts.append(f"Vendor: {transaction_data['vendor']}")
        
        if 'category' in transaction_data and transaction_data['category']:
            text_parts.append(f"Category: {transaction_data['category']}")
        
        if 'amount' in transaction_data:
            amount = transaction_data['amount']
            magnitude = "small" if float(amount) < 100 else "medium" if float(amount) < 1000 else "large"
            text_parts.append(f"Amount: {magnitude}")
        
        text = " | ".join(text_parts)
        return self.generate_embedding(text)
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1, vec2: Embedding vectors
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm_v1 = np.linalg.norm(v1)
            norm_v2 = np.linalg.norm(v2)
            
            if norm_v1 == 0 or norm_v2 == 0:
                return 0.0
            
            return float(dot_product / (norm_v1 * norm_v2))
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    def find_similar_transactions(
        self,
        query_embedding: List[float],
        company_id: str,
        top_k: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict]:
        """
        Find similar transactions using vector similarity.
        
        Args:
            query_embedding: Embedding vector to search for
            company_id: Company ID to filter by
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar transactions with similarity scores
        """
        from transactions.models import Transaction
        
        try:
            # Get validated transactions with embeddings
            transactions = Transaction.objects.filter(
                company_id=company_id,
                is_validated=True,
                embedding__isnull=False
            ).select_related('account').order_by('-date')[:200]  # Last 200 transactions
            
            # Calculate similarities
            similarities = []
            for transaction in transactions:
                if transaction.embedding:
                    similarity = self.cosine_similarity(query_embedding, transaction.embedding)
                    if similarity >= min_similarity:
                        similarities.append({
                            'transaction': transaction,
                            'similarity': similarity
                        })
            
            # Sort by similarity and take top_k
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            results = similarities[:top_k]
            
            # Format results
            formatted = []
            for result in results:
                trans = result['transaction']
                formatted.append({
                    'id': str(trans.id),
                    'date': trans.date.isoformat(),
                    'description': trans.description,
                    'amount': float(trans.amount),
                    'account_code': trans.account.account_code if trans.account else None,
                    'account_name': trans.account.account_name if trans.account else None,
                    'similarity': round(result['similarity'], 3)
                })
            
            return formatted
        except Exception as e:
            logger.error(f"Failed to find similar transactions: {e}")
            return []
    
    def augment_prompt_with_context(
        self,
        transaction_data: Dict,
        company_id: str,
        max_examples: int = 5
    ) -> str:
        """
        Create an augmented prompt with relevant historical context.
        
        Args:
            transaction_data: Transaction to classify
            company_id: Company ID
            max_examples: Maximum number of examples to include
            
        Returns:
            Augmented prompt string
        """
        # Generate embedding for query
        query_embedding = self.generate_transaction_embedding(transaction_data)
        
        if not query_embedding:
            # Fallback to basic prompt
            return self._create_basic_prompt(transaction_data)
        
        # Find similar transactions
        similar = self.find_similar_transactions(
            query_embedding,
            company_id,
            top_k=max_examples
        )
        
        # Build augmented prompt
        prompt_parts = [
            "You are a financial transaction classifier. Classify the following transaction based on similar historical patterns.",
            "",
            "## Historical Examples (Similar Transactions):"
        ]
        
        if similar:
            for i, example in enumerate(similar, 1):
                prompt_parts.append(
                    f"\n{i}. Description: {example['description']}"
                    f"\n   Amount: ${example['amount']:.2f}"
                    f"\n   Account: {example['account_code']} - {example['account_name']}"
                    f"\n   Similarity: {example['similarity']:.1%}"
                )
        else:
            prompt_parts.append("\nNo similar historical transactions found.")
        
        prompt_parts.extend([
            "",
            "## Transaction to Classify:",
            f"Description: {transaction_data.get('description', 'N/A')}",
            f"Amount: ${transaction_data.get('amount', 0):.2f}",
            f"Vendor: {transaction_data.get('vendor', 'N/A')}",
            "",
            "Based on the historical patterns above, suggest the most appropriate account classification.",
            "Return a JSON object with: account_code, account_name, confidence (0-1), reasoning"
        ])
        
        return "\n".join(prompt_parts)
    
    def _create_basic_prompt(self, transaction_data: Dict) -> str:
        """Create basic prompt without RAG context."""
        return f"""Classify this transaction:
Description: {transaction_data.get('description', 'N/A')}
Amount: ${transaction_data.get('amount', 0):.2f}
Vendor: {transaction_data.get('vendor', 'N/A')}

Suggest appropriate account classification as JSON:
{{"account_code": "XXXX", "account_name": "Name", "confidence": 0.0, "reasoning": "..."}}"""
    
    def store_transaction_embedding(self, transaction_id: str, embedding: List[float]):
        """
        Store transaction embedding in database.
        
        Args:
            transaction_id: Transaction ID
            embedding: Embedding vector
        """
        from transactions.models import Transaction
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            transaction.embedding = embedding
            transaction.save(update_fields=['embedding'])
            logger.info(f"Stored embedding for transaction {transaction_id}")
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
    
    def batch_generate_embeddings(self, company_id: str, limit: int = 100):
        """
        Generate embeddings for transactions without embeddings.
        
        Args:
            company_id: Company ID
            limit: Maximum number of transactions to process
            
        Returns:
            Number of embeddings generated
        """
        from transactions.models import Transaction
        
        try:
            # Get transactions without embeddings
            transactions = Transaction.objects.filter(
                company_id=company_id,
                embedding__isnull=True,
                is_validated=True
            ).order_by('-date')[:limit]
            
            count = 0
            for transaction in transactions:
                transaction_data = {
                    'description': transaction.description,
                    'vendor': transaction.vendor or '',
                    'amount': float(transaction.amount),
                    'category': transaction.category or ''
                }
                
                embedding = self.generate_transaction_embedding(transaction_data)
                if embedding:
                    self.store_transaction_embedding(str(transaction.id), embedding)
                    count += 1
            
            logger.info(f"Generated {count} embeddings for company {company_id}")
            return count
        except Exception as e:
            logger.error(f"Failed to batch generate embeddings: {e}")
            return 0
    
    def normalize_vendor(self, vendor_name: str, company_id: str) -> Optional[str]:
        """
        Normalize vendor name using similarity search.
        
        Args:
            vendor_name: Raw vendor name
            company_id: Company ID
            
        Returns:
            Canonical vendor name or None
        """
        if not vendor_name:
            return None
        
        # Generate embedding for vendor
        embedding = self.generate_embedding(f"Vendor: {vendor_name}")
        if not embedding:
            return vendor_name
        
        # Find similar vendors
        similar = self.find_similar_transactions(
            embedding,
            company_id,
            top_k=3,
            min_similarity=0.85
        )
        
        if similar:
            # Use most similar vendor name
            return similar[0]['description'].split(' - ')[0] if ' - ' in similar[0]['description'] else vendor_name
        
        return vendor_name
    
    def get_service_stats(self) -> Dict:
        """Get RAG service statistics."""
        from transactions.models import Transaction
        
        total_transactions = Transaction.objects.count()
        with_embeddings = Transaction.objects.filter(embedding__isnull=False).count()
        
        return {
            'model_loaded': self._model is not None,
            'embedding_dimension': self._embedding_dim if self._model else None,
            'total_transactions': total_transactions,
            'transactions_with_embeddings': with_embeddings,
            'coverage': round(with_embeddings / total_transactions * 100, 1) if total_transactions > 0 else 0
        }


# Singleton instance
rag_service = RAGService()
