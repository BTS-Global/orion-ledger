"""
Views for AI-powered features: RAG, Feedback, and Active Learning.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from companies.models import Company
from transactions.models import Transaction
from core.rag_service import rag_service
from core.feedback_service import FeedbackService
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_feedback(request, company_id):
    """
    Record user feedback on AI prediction.
    
    POST /api/companies/{company_id}/ai/feedback/
    Body:
    {
        "transaction_id": "uuid",
        "predicted_account_id": "uuid" (optional),
        "corrected_account_id": "uuid",
        "predicted_confidence": 0.85,
        "reason": "Description was clearer" (optional)
    }
    """
    try:
        company = get_object_or_404(Company, id=company_id)
        
        transaction_id = request.data.get('transaction_id')
        predicted_account_id = request.data.get('predicted_account_id')
        corrected_account_id = request.data.get('corrected_account_id')
        predicted_confidence = request.data.get('predicted_confidence', 0.0)
        reason = request.data.get('reason', '')
        
        if not transaction_id or not corrected_account_id:
            return Response(
                {'error': 'transaction_id and corrected_account_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Record feedback
        feedback = FeedbackService.record_correction(
            transaction_id=transaction_id,
            predicted_account_id=predicted_account_id,
            corrected_account_id=corrected_account_id,
            predicted_confidence=predicted_confidence,
            user=request.user,
            reason=reason
        )
        
        return Response({
            'success': True,
            'feedback_id': str(feedback.id),
            'feedback_type': feedback.feedback_type,
            'message': 'Feedback recorded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_low_confidence_transactions(request, company_id):
    """
    Get transactions with low confidence scores for active learning.
    
    GET /api/companies/{company_id}/ai/low-confidence/?limit=20
    """
    try:
        company = get_object_or_404(Company, id=company_id)
        limit = int(request.GET.get('limit', 20))
        
        transactions = FeedbackService.get_low_confidence_transactions(
            str(company_id),
            limit=limit
        )
        
        return Response({
            'count': len(transactions),
            'transactions': transactions
        })
        
    except Exception as e:
        logger.error(f"Error getting low confidence transactions: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accuracy_metrics(request, company_id):
    """
    Get AI accuracy metrics and trends.
    
    GET /api/companies/{company_id}/ai/metrics/?days=30
    """
    try:
        company = get_object_or_404(Company, id=company_id)
        days = int(request.GET.get('days', 30))
        
        # Get accuracy trend
        trend = FeedbackService.get_accuracy_trend(str(company_id), days=days)
        
        # Get feedback summary
        summary = FeedbackService.get_feedback_summary(str(company_id))
        
        # Get retraining recommendation
        retraining = FeedbackService.suggest_retraining(str(company_id))
        
        return Response({
            'trend': trend,
            'summary': summary,
            'retraining_recommendation': retraining
        })
        
    except Exception as e:
        logger.error(f"Error getting accuracy metrics: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_similar_transactions(request, company_id):
    """
    Find similar transactions using semantic search.
    
    GET /api/companies/{company_id}/ai/similar/?description=Coffee&amount=5.50&top_k=5
    """
    try:
        company = get_object_or_404(Company, id=company_id)
        
        description = request.GET.get('description', '')
        amount = float(request.GET.get('amount', 0))
        vendor = request.GET.get('vendor', '')
        top_k = int(request.GET.get('top_k', 5))
        
        if not description:
            return Response(
                {'error': 'description parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate embedding for query
        transaction_data = {
            'description': description,
            'amount': amount,
            'vendor': vendor
        }
        
        embedding = rag_service.generate_transaction_embedding(transaction_data)
        
        if not embedding:
            return Response(
                {'error': 'Failed to generate embedding'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Find similar transactions
        similar = rag_service.find_similar_transactions(
            embedding,
            str(company_id),
            top_k=top_k
        )
        
        return Response({
            'query': transaction_data,
            'similar_transactions': similar,
            'count': len(similar)
        })
        
    except Exception as e:
        logger.error(f"Error finding similar transactions: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_embeddings(request, company_id):
    """
    Generate embeddings for transactions without embeddings.
    
    POST /api/companies/{company_id}/ai/generate-embeddings/
    Body: {"limit": 100}
    """
    try:
        company = get_object_or_404(Company, id=company_id)
        limit = int(request.data.get('limit', 100))
        
        count = rag_service.batch_generate_embeddings(str(company_id), limit=limit)
        
        return Response({
            'success': True,
            'embeddings_generated': count,
            'message': f'Generated {count} embeddings'
        })
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rag_stats(request, company_id):
    """
    Get RAG service statistics.
    
    GET /api/companies/{company_id}/ai/rag-stats/
    """
    try:
        company = get_object_or_404(Company, id=company_id)
        
        stats = rag_service.get_service_stats()
        
        return Response(stats)
        
    except Exception as e:
        logger.error(f"Error getting RAG stats: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def classify_with_rag(request, company_id):
    """
    Classify a transaction using RAG-enhanced context.
    
    POST /api/companies/{company_id}/ai/classify/
    Body:
    {
        "description": "Coffee at Starbucks",
        "amount": 5.50,
        "vendor": "Starbucks",
        "max_examples": 5
    }
    """
    try:
        company = get_object_or_404(Company, id=company_id)
        
        description = request.data.get('description', '')
        amount = float(request.data.get('amount', 0))
        vendor = request.data.get('vendor', '')
        max_examples = int(request.data.get('max_examples', 5))
        
        if not description:
            return Response(
                {'error': 'description is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction_data = {
            'description': description,
            'amount': amount,
            'vendor': vendor
        }
        
        # Get RAG-augmented prompt
        prompt = rag_service.augment_prompt_with_context(
            transaction_data,
            str(company_id),
            max_examples=max_examples
        )
        
        # Generate embedding
        embedding = rag_service.generate_transaction_embedding(transaction_data)
        
        # Find similar transactions
        similar = []
        if embedding:
            similar = rag_service.find_similar_transactions(
                embedding,
                str(company_id),
                top_k=3
            )
        
        # Get suggestion from most similar
        suggestion = None
        if similar:
            best_match = similar[0]
            suggestion = {
                'account_code': best_match['account_code'],
                'account_name': best_match['account_name'],
                'confidence': best_match['similarity'],
                'source': 'RAG'
            }
        
        return Response({
            'transaction': transaction_data,
            'suggestion': suggestion,
            'similar_transactions': similar,
            'augmented_prompt': prompt
        })
        
    except Exception as e:
        logger.error(f"Error classifying with RAG: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
