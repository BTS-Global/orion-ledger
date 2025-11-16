"""
Feedback Loop and Active Learning System for Orion Ledger.

This module handles:
- User corrections and feedback
- Active learning for low-confidence predictions
- Performance metrics tracking
- Model improvement over time
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.contrib.auth.models import User

from core.models import FeedbackEntry, PredictionMetrics

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for managing feedback and active learning."""
    
    @staticmethod
    def record_correction(
        transaction_id: str,
        predicted_account_id: Optional[str],
        corrected_account_id: str,
        predicted_confidence: float,
        user: User,
        reason: str = ""
    ) -> FeedbackEntry:
        """
        Record a user correction.
        
        Args:
            transaction_id: Transaction ID
            predicted_account_id: Originally predicted account ID
            corrected_account_id: Corrected account ID
            predicted_confidence: Original confidence score
            user: User who made the correction
            reason: Optional reason for correction
            
        Returns:
            FeedbackEntry instance
        """
        from transactions.models import Transaction
        from companies.models import ChartOfAccounts
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            corrected_account = ChartOfAccounts.objects.get(id=corrected_account_id)
            predicted_account = None
            
            if predicted_account_id:
                try:
                    predicted_account = ChartOfAccounts.objects.get(id=predicted_account_id)
                except ChartOfAccounts.DoesNotExist:
                    pass
            
            # Determine feedback type
            if predicted_account and predicted_account.id == corrected_account.id:
                feedback_type = 'CONFIRMATION'
            elif predicted_account:
                feedback_type = 'CORRECTION'
            else:
                feedback_type = 'REJECTION'
            
            # Create feedback entry
            feedback = FeedbackEntry.objects.create(
                transaction=transaction,
                user=user,
                predicted_account=predicted_account,
                predicted_confidence=predicted_confidence,
                corrected_account=corrected_account,
                feedback_type=feedback_type,
                correction_reason=reason
            )
            
            # Update transaction
            transaction.account = corrected_account
            transaction.is_validated = True
            transaction.save()
            
            # Regenerate embedding with corrected data
            FeedbackService._update_transaction_embedding(transaction)
            
            # Update metrics
            FeedbackService._update_metrics(transaction.company, feedback)
            
            logger.info(f"Recorded {feedback_type} feedback for transaction {transaction_id}")
            return feedback
            
        except Exception as e:
            logger.error(f"Failed to record correction: {e}")
            raise
    
    @staticmethod
    def _update_transaction_embedding(transaction):
        """Update transaction embedding with corrected data."""
        try:
            from core.rag_service import rag_service
            
            transaction_data = {
                'description': transaction.description,
                'vendor': transaction.vendor or '',
                'amount': float(transaction.amount),
                'category': transaction.account.account_name if transaction.account else ''
            }
            
            embedding = rag_service.generate_transaction_embedding(transaction_data)
            if embedding:
                transaction.embedding = embedding
                transaction.save(update_fields=['embedding'])
                logger.info(f"Updated embedding for transaction {transaction.id}")
        except Exception as e:
            logger.error(f"Failed to update embedding: {e}")
    
    @staticmethod
    def _update_metrics(company, feedback: FeedbackEntry):
        """Update prediction metrics based on feedback."""
        try:
            today = timezone.now().date()
            
            metrics, created = PredictionMetrics.objects.get_or_create(
                company=company,
                date=today,
                defaults={
                    'total_predictions': 0,
                    'correct_predictions': 0,
                    'incorrect_predictions': 0,
                    'avg_confidence': 0.0
                }
            )
            
            metrics.total_predictions += 1
            
            if feedback.feedback_type in ['CONFIRMATION', 'CORRECTION']:
                is_correct = feedback.feedback_type == 'CONFIRMATION'
                
                if is_correct:
                    metrics.correct_predictions += 1
                else:
                    metrics.incorrect_predictions += 1
                
                confidence = feedback.predicted_confidence
                
                # Update detailed metrics
                if confidence > 0.8:
                    if is_correct:
                        metrics.high_confidence_correct += 1
                    else:
                        metrics.high_confidence_incorrect += 1
                elif confidence < 0.6:
                    if is_correct:
                        metrics.low_confidence_correct += 1
                    else:
                        metrics.low_confidence_incorrect += 1
            
            # Recalculate average confidence
            feedbacks = FeedbackEntry.objects.filter(
                transaction__company=company,
                timestamp__date=today
            )
            if feedbacks.exists():
                metrics.avg_confidence = feedbacks.aggregate(
                    avg=Avg('predicted_confidence')
                )['avg'] or 0.0
            
            metrics.save()
            logger.info(f"Updated metrics for {company.name}")
            
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    @staticmethod
    def get_low_confidence_transactions(company_id: str, limit: int = 20) -> List[Dict]:
        """
        Get transactions with low confidence scores for active learning.
        
        Args:
            company_id: Company ID
            limit: Maximum number of results
            
        Returns:
            List of transactions needing review
        """
        from transactions.models import Transaction
        
        try:
            transactions = Transaction.objects.filter(
                company_id=company_id,
                is_validated=False,
                confidence_score__lt=0.7,
                confidence_score__gt=0.0
            ).select_related('account').order_by('confidence_score')[:limit]
            
            results = []
            for trans in transactions:
                results.append({
                    'id': str(trans.id),
                    'date': trans.date.isoformat(),
                    'description': trans.description,
                    'amount': float(trans.amount),
                    'suggested_account': {
                        'code': trans.account.account_code,
                        'name': trans.account.account_name
                    } if trans.account else None,
                    'confidence': round(trans.confidence_score, 3),
                    'priority': 'high' if trans.confidence_score < 0.5 else 'medium'
                })
            
            return results
        except Exception as e:
            logger.error(f"Failed to get low confidence transactions: {e}")
            return []
    
    @staticmethod
    def get_accuracy_trend(company_id: str, days: int = 30) -> List[Dict]:
        """
        Get accuracy trend over time.
        
        Args:
            company_id: Company ID
            days: Number of days to look back
            
        Returns:
            List of daily accuracy metrics
        """
        try:
            start_date = timezone.now().date() - timedelta(days=days)
            
            metrics = PredictionMetrics.objects.filter(
                company_id=company_id,
                date__gte=start_date
            ).order_by('date')
            
            trend = []
            for metric in metrics:
                trend.append({
                    'date': metric.date.isoformat(),
                    'accuracy': round(metric.accuracy, 1),
                    'total_predictions': metric.total_predictions,
                    'avg_confidence': round(metric.avg_confidence, 3),
                    'high_confidence_correct': metric.high_confidence_correct,
                    'high_confidence_incorrect': metric.high_confidence_incorrect
                })
            
            return trend
        except Exception as e:
            logger.error(f"Failed to get accuracy trend: {e}")
            return []
    
    @staticmethod
    def get_feedback_summary(company_id: str) -> Dict:
        """
        Get summary of feedback activity.
        
        Args:
            company_id: Company ID
            
        Returns:
            Summary statistics
        """
        try:
            from transactions.models import Transaction
            
            # Get all feedbacks for company
            feedbacks = FeedbackEntry.objects.filter(
                transaction__company_id=company_id
            )
            
            total = feedbacks.count()
            corrections = feedbacks.filter(feedback_type='CORRECTION').count()
            confirmations = feedbacks.filter(feedback_type='CONFIRMATION').count()
            rejections = feedbacks.filter(feedback_type='REJECTION').count()
            
            # Get most recent metrics
            latest_metrics = PredictionMetrics.objects.filter(
                company_id=company_id
            ).order_by('-date').first()
            
            return {
                'total_feedbacks': total,
                'corrections': corrections,
                'confirmations': confirmations,
                'rejections': rejections,
                'correction_rate': round(corrections / total * 100, 1) if total > 0 else 0,
                'confirmation_rate': round(confirmations / total * 100, 1) if total > 0 else 0,
                'current_accuracy': round(latest_metrics.accuracy, 1) if latest_metrics else 0,
                'current_avg_confidence': round(latest_metrics.avg_confidence, 3) if latest_metrics else 0
            }
        except Exception as e:
            logger.error(f"Failed to get feedback summary: {e}")
            return {}
    
    @staticmethod
    def suggest_retraining(company_id: str) -> Dict:
        """
        Analyze if model retraining is recommended.
        
        Args:
            company_id: Company ID
            
        Returns:
            Recommendation dict
        """
        try:
            # Get recent metrics (last 7 days)
            week_ago = timezone.now().date() - timedelta(days=7)
            recent_metrics = PredictionMetrics.objects.filter(
                company_id=company_id,
                date__gte=week_ago
            )
            
            if not recent_metrics.exists():
                return {
                    'should_retrain': False,
                    'reason': 'Insufficient data for evaluation'
                }
            
            # Calculate average accuracy
            avg_accuracy = recent_metrics.aggregate(
                avg=Avg('correct_predictions') / Avg('total_predictions') * 100
            )
            
            # Count corrections
            corrections = FeedbackEntry.objects.filter(
                transaction__company_id=company_id,
                feedback_type='CORRECTION',
                timestamp__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            # Decision logic
            should_retrain = False
            reasons = []
            
            if corrections > 50:
                should_retrain = True
                reasons.append(f"High number of corrections in last 7 days: {corrections}")
            
            if avg_accuracy and avg_accuracy['avg'] < 70:
                should_retrain = True
                reasons.append(f"Low accuracy: {avg_accuracy['avg']:.1f}%")
            
            return {
                'should_retrain': should_retrain,
                'reasons': reasons,
                'corrections_last_week': corrections,
                'avg_accuracy_last_week': round(avg_accuracy['avg'], 1) if avg_accuracy else 0
            }
        except Exception as e:
            logger.error(f"Failed to suggest retraining: {e}")
            return {'should_retrain': False, 'reason': str(e)}
