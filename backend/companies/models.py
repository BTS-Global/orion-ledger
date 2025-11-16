from django.db import models
from django.contrib.auth.models import User
import uuid


class Company(models.Model):
    """Model representing a company in the system."""
    
    # Jurisdictions supported
    JURISDICTION_CHOICES = [
        # North America
        ('US', 'United States'),
        ('CA', 'Canada'),
        
        # Caribbean Offshore
        ('BVI', 'British Virgin Islands'),
        ('KY', 'Cayman Islands'),
        ('BS', 'Bahamas'),
        ('SC', 'Seychelles'),
        ('PA', 'Panama'),
        ('BZ', 'Belize'),
        ('AG', 'Antigua and Barbuda'),
        ('DM', 'Dominica'),
        ('KN', 'Saint Kitts and Nevis'),
        ('VC', 'Saint Vincent and the Grenadines'),
        
        # Europe
        ('GB', 'United Kingdom'),
        ('IE', 'Ireland'),
        ('LU', 'Luxembourg'),
        ('MT', 'Malta'),
        ('CY', 'Cyprus'),
        
        # South America
        ('BR', 'Brazil'),
        ('UY', 'Uruguay'),
        
        # Asia
        ('SG', 'Singapore'),
        ('HK', 'Hong Kong'),
        
        # Other
        ('OTHER', 'Other'),
    ]
    
    # Entity types
    ENTITY_TYPE_CHOICES = [
        # US
        ('US_LLC', 'US LLC'),
        ('US_C_CORP', 'US C-Corporation'),
        ('US_S_CORP', 'US S-Corporation'),
        ('US_PARTNERSHIP', 'US Partnership'),
        ('US_SOLE_PROP', 'US Sole Proprietorship'),
        
        # Offshore
        ('IBC', 'International Business Company'),
        ('FOUNDATION', 'Foundation'),
        ('TRUST', 'Trust'),
        ('LIMITED', 'Limited Company'),
        ('EXEMPTED', 'Exempted Company'),
        ('LLC_OFFSHORE', 'Offshore LLC'),
        
        # Brazil
        ('BR_LTDA', 'Sociedade Limitada (LTDA)'),
        ('BR_SA', 'Sociedade Anônima (S.A.)'),
        ('BR_EIRELI', 'EIRELI'),
        
        # Other
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    
    # Jurisdiction and entity type (NEW)
    jurisdiction = models.CharField(
        max_length=10,
        choices=JURISDICTION_CHOICES,
        default='US',
        help_text="Jurisdiction where the company is incorporated"
    )
    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPE_CHOICES,
        default='US_LLC',
        help_text="Type of legal entity"
    )
    
    # Tax identification (flexible for different jurisdictions)
    tax_id = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Tax ID (EIN for US, CNPJ for Brazil, Company Number for offshore, etc.)"
    )
    
    # Incorporation details (NEW)
    incorporation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of incorporation/formation"
    )
    registration_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Company registration number (if different from tax_id)"
    )
    
    fiscal_year_start = models.DateField(help_text="Start date of the fiscal year")
    
    # Address fields
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(
        max_length=100, 
        blank=True,
        help_text="State/Province/Region"
    )
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(
        max_length=100,
        default='United States',
        help_text="Country name"
    )
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Registered Agent / Registered Office (for offshore entities)
    registered_agent_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Registered agent or registered office name"
    )
    registered_agent_address = models.TextField(
        blank=True,
        help_text="Registered agent or registered office address"
    )
    
    # Corporate Services tracking (NEW)
    client_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Client reference number for corporate services providers"
    )
    annual_renewal_date = models.DateField(
        null=True,
        blank=True,
        help_text="Next annual renewal date"
    )
    annual_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual renewal fee"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Currency for fees and accounting (ISO 4217 code)"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the company is currently active"
    )
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about this company"
    )
    
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
        return f"{self.name} ({self.jurisdiction})"
    
    def is_offshore(self):
        """Check if this is an offshore jurisdiction."""
        offshore_jurisdictions = ['BVI', 'KY', 'BS', 'SC', 'PA', 'BZ', 'AG', 'DM', 'KN', 'VC']
        return self.jurisdiction in offshore_jurisdictions
    
    def is_us_entity(self):
        """Check if this is a US entity."""
        return self.jurisdiction == 'US'
    
    def days_until_renewal(self):
        """Calculate days until annual renewal."""
        if not self.annual_renewal_date:
            return None
        from django.utils import timezone
        delta = self.annual_renewal_date - timezone.now().date()
        return delta.days


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
    
    # Multi-currency support (NEW)
    currency = models.CharField(
        max_length=3,
        blank=True,
        help_text="Specific currency for this account (if different from company default). ISO 4217 code."
    )
    allow_multi_currency = models.BooleanField(
        default=False,
        help_text="If True, this account can hold transactions in multiple currencies"
    )
    
    # IRS form mapping (JSON field to map to specific boxes in IRS forms)
    irs_box_mapping = models.JSONField(
        null=True, 
        blank=True, 
        help_text="Mapping to IRS form boxes (for US entities)"
    )
    
    # Offshore/tax reporting mapping (NEW)
    tax_reporting_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Category for tax reporting (varies by jurisdiction)"
    )
    
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

