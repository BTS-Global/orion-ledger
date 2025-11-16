from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from companies.models import Company
import uuid


class Document(models.Model):
    """Model for uploaded documents (bank statements, receipts, etc.)."""
    
    STATUS_CHOICES = [
        ('UPLOADED', 'Uploaded'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('READY_FOR_REVIEW', 'Ready for Review'),
    ]
    
    FILE_TYPES = [
        ('PDF', 'PDF'),
        ('CSV', 'CSV'),
        ('JPG', 'JPG'),
        ('PNG', 'PNG'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='documents')
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPLOADED')
    processing_result = models.JSONField(null=True, blank=True, help_text="Results from extraction process")
    error_message = models.TextField(blank=True)
    
    # New fields for improved processing
    processing_progress = models.JSONField(default=dict, blank=True, help_text="Current processing progress")
    error_log = models.TextField(blank=True, null=True, help_text="Detailed error log")
    processing_attempts = models.IntegerField(default=0, help_text="Number of processing attempts")
    extracted_data = models.JSONField(default=dict, blank=True, help_text="Extracted data pending review")
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    upload_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['upload_date']),
        ]
    
    def __str__(self):
        return f"{self.file_name} ({self.status})"
    
    def update_progress(self, stage, progress, message=""):
        """Update processing progress"""
        self.processing_progress = {
            'stage': stage,
            'progress': progress,
            'message': message,
            'updated_at': timezone.now().isoformat()
        }
        self.save(update_fields=['processing_progress', 'updated_at'])
    
    def log_error(self, error_message, error_type=""):
        """Log processing error"""
        timestamp = timezone.now().isoformat()
        error_entry = f"[{timestamp}] {error_type}: {error_message}\n"
        self.error_log = error_entry + (self.error_log or "")
        self.status = 'FAILED'
        self.processing_attempts += 1
        self.save(update_fields=['error_log', 'status', 'processing_attempts', 'updated_at'])
    
    def can_retry(self):
        """Check if document can be retried"""
        return self.processing_attempts < 3

