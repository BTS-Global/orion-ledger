from django.db import models
from django.contrib.auth.models import User
import uuid


class AuditLog(models.Model):
    """Model for audit trail of all significant actions."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='audit_logs'
    )
    action = models.CharField(max_length=100, help_text="Action performed")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(help_text="Additional details about the action")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Object tracking
    content_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"


class FeedbackEntry(models.Model):
    """Store user feedback on AI predictions for active learning."""
    
    FEEDBACK_TYPES = [
        ('CORRECTION', 'Correction'),
        ('CONFIRMATION', 'Confirmation'),
        ('REJECTION', 'Rejection'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Prediction details
    predicted_account = models.ForeignKey(
        'companies.ChartOfAccounts',
        on_delete=models.SET_NULL,
        null=True,
        related_name='predicted_for'
    )
    predicted_confidence = models.FloatField(default=0.0)
    
    # Correction details
    corrected_account = models.ForeignKey(
        'companies.ChartOfAccounts',
        on_delete=models.SET_NULL,
        null=True,
        related_name='corrected_to'
    )
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    
    # Context
    correction_reason = models.TextField(blank=True, help_text="Why was the prediction wrong?")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['transaction', 'feedback_type']),
            models.Index(fields=['timestamp']),
        ]
        verbose_name_plural = "Feedback entries"
    
    def __str__(self):
        return f"Feedback on {self.transaction.description[:50]} at {self.timestamp}"


class PredictionMetrics(models.Model):
    """Track AI prediction performance over time."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    
    # Time period
    date = models.DateField()
    
    # Metrics
    total_predictions = models.IntegerField(default=0)
    correct_predictions = models.IntegerField(default=0)
    incorrect_predictions = models.IntegerField(default=0)
    avg_confidence = models.FloatField(default=0.0)
    
    # Detailed metrics
    high_confidence_correct = models.IntegerField(
        default=0,
        help_text="Correct with >0.8 confidence"
    )
    high_confidence_incorrect = models.IntegerField(
        default=0,
        help_text="Incorrect with >0.8 confidence"
    )
    low_confidence_correct = models.IntegerField(
        default=0,
        help_text="Correct with <0.6 confidence"
    )
    low_confidence_incorrect = models.IntegerField(
        default=0,
        help_text="Incorrect with <0.6 confidence"
    )
    
    # Processing
    avg_processing_time = models.FloatField(
        default=0.0,
        help_text="Average time in seconds"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['company', 'date']]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['date']),
        ]
        verbose_name_plural = "Prediction metrics"
    
    def __str__(self):
        accuracy = (
            self.correct_predictions / self.total_predictions * 100
            if self.total_predictions > 0
            else 0
        )
        return f"{self.company.name} - {self.date} - {accuracy:.1f}% accuracy"
    
    @property
    def accuracy(self):
        """Calculate accuracy percentage."""
        if self.total_predictions == 0:
            return 0.0
        return (self.correct_predictions / self.total_predictions) * 100

