from django.db import models
from django.contrib.auth.models import User
from companies.models import Company
import uuid


class Document(models.Model):
    """Model for uploaded documents (bank statements, receipts, etc.)."""
    
    STATUS_CHOICES = [
        ('UPLOADED', 'Uploaded'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
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
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    upload_date = models.DateTimeField(auto_now_add=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.file_name} ({self.status})"

