"""
Models for IRS tax forms.
"""
from django.db import models
from django.contrib.auth.models import User
from companies.models import Company


class IRSForm(models.Model):
    """Base model for IRS tax forms."""
    
    FORM_TYPES = [
        ('5472', 'Form 5472 - Information Return'),
        ('1099-NEC', 'Form 1099-NEC - Nonemployee Compensation'),
        ('1120', 'Form 1120 - Corporate Income Tax Return'),
        ('1040', 'Form 1040 - Individual Income Tax Return'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('READY', 'Ready to File'),
        ('FILED', 'Filed'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='irs_forms')
    form_type = models.CharField(max_length=20, choices=FORM_TYPES)
    tax_year = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Form data stored as JSON
    form_data = models.JSONField(default=dict)
    
    # Generated PDF file
    pdf_file = models.FileField(upload_to='irs_forms/', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_forms')
    filed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-tax_year', '-created_at']
        unique_together = ['company', 'form_type', 'tax_year']
    
    def __str__(self):
        return f"{self.form_type} - {self.company.company_name} - {self.tax_year}"

