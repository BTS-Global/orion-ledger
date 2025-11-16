from django.db import models
from django.contrib.auth.models import User
import uuid
import secrets


class APIKey(models.Model):
    """API keys for MCP server authentication."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=64, unique=True, db_index=True)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_api_keys'
    )
    name = models.CharField(max_length=100, help_text="Friendly name for this API key")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Permissions
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    can_classify = models.BooleanField(default=True)
    can_audit = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key', 'is_active']),
            models.Index(fields=['company', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.company.name}"
    
    @staticmethod
    def generate_key():
        """Generate a secure random API key."""
        return f"orion_mcp_{secrets.token_urlsafe(32)}"
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    """Model for audit trail of all significant actions."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='audit_logs'
    )
    
    # MCP-specific fields
    company_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    request_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    service = models.CharField(max_length=50, default='web', help_text="Service that generated the log")
    method = models.CharField(max_length=10, blank=True)
    path = models.CharField(max_length=500, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(default=True)
    
    # Original fields
    action = models.CharField(max_length=100, help_text="Action performed")
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    details = models.JSONField(default=dict, help_text="Additional details about the action")
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
            models.Index(fields=['company_id', 'timestamp']),
            models.Index(fields=['service', 'timestamp']),
        ]
    
    def __str__(self):
        if self.service == 'mcp-server':
            return f"[MCP] {self.timestamp} - {self.company_id} - {self.method} {self.path}"
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


class AIPrediction(models.Model):
    """Store AI predictions for learning and improvement."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.CharField(max_length=100, db_index=True)
    
    # Input data
    transaction_data = models.JSONField(help_text="Original transaction data")
    
    # Prediction
    predicted_account = models.CharField(max_length=50)
    confidence = models.FloatField()
    reasoning = models.TextField(blank=True)
    model_used = models.CharField(max_length=50, default='claude-3-sonnet')
    
    # Feedback
    was_correct = models.BooleanField(null=True, blank=True)
    actual_account = models.CharField(max_length=50, null=True, blank=True)
    feedback_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    embedding = models.JSONField(null=True, blank=True, help_text="Vector embedding for similarity search")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_id', 'created_at']),
            models.Index(fields=['predicted_account', 'confidence']),
            models.Index(fields=['was_correct']),
        ]
    
    def __str__(self):
        return f"Prediction: {self.predicted_account} ({self.confidence:.2f})"

