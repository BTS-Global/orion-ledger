from django.db import models
from django.contrib.auth.models import User
import uuid


class Company(models.Model):
    """Model representing a company in the system."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=20, unique=True, help_text="EIN (Employer Identification Number)")
    fiscal_year_start = models.DateField(help_text="Start date of the fiscal year")
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2, help_text="Two-letter state code")
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_companies')
    users = models.ManyToManyField(User, related_name='companies', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.tax_id})"


class UserProfile(models.Model):
    """Extended user profile with accounting-specific information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    active_company = models.ForeignKey(
        Company, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL, 
        related_name='active_users'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} ({self.user.email})"


class ChartOfAccounts(models.Model):
    """Chart of Accounts for each company."""
    
    ACCOUNT_TYPES = [
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('REVENUE', 'Revenue'),
        ('EXPENSE', 'Expense'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='accounts')
    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    description = models.TextField(blank=True)
    parent_account = models.ForeignKey(
        'self', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL, 
        related_name='sub_accounts'
    )
    
    # Hierarchical fields
    level = models.IntegerField(
        default=1,
        help_text="Account level in hierarchy (1-5)"
    )
    is_group_account = models.BooleanField(
        default=False,
        help_text="True if this is a group account (non-transactional)"
    )
    normal_balance = models.CharField(
        max_length=10,
        choices=[('debit', 'Debit'), ('credit', 'Credit')],
        default='debit',
        help_text="Normal balance side for this account"
    )
    
    # IRS form mapping (JSON field to map to specific boxes in IRS forms)
    irs_box_mapping = models.JSONField(null=True, blank=True, help_text="Mapping to IRS form boxes")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Chart of Accounts"
        ordering = ['account_code']
        unique_together = ['company', 'account_code']
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"

