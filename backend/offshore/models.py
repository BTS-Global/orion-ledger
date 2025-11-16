from django.db import models
from django.contrib.auth.models import User
from companies.models import Company
import uuid


class AnnualReturn(models.Model):
    """Annual Return filing for offshore entities."""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('FILED', 'Filed'),
        ('REJECTED', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='annual_returns')
    
    # Filing details
    filing_year = models.IntegerField(help_text="Year for this annual return")
    due_date = models.DateField(help_text="Due date for this filing")
    filed_date = models.DateField(null=True, blank=True, help_text="Date when filed")
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Registry reference number (if applicable)"
    )
    
    # Financial summary (simplified for offshore entities)
    total_assets = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total assets at year end"
    )
    total_liabilities = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total liabilities at year end"
    )
    total_equity = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total equity at year end"
    )
    net_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net income for the year"
    )
    
    # Documents
    pdf_file = models.FileField(
        upload_to='annual_returns/',
        null=True,
        blank=True,
        help_text="Generated PDF of the annual return"
    )
    supporting_documents = models.JSONField(
        null=True,
        blank=True,
        help_text="List of supporting document paths"
    )
    
    # Metadata
    notes = models.TextField(blank=True, help_text="Internal notes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_annual_returns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-filing_year', '-due_date']
        unique_together = ['company', 'filing_year']
    
    def __str__(self):
        return f"{self.company.name} - Annual Return {self.filing_year}"
    
    def is_overdue(self):
        """Check if the filing is overdue."""
        from django.utils import timezone
        if self.status in ['FILED', 'APPROVED']:
            return False
        return timezone.now().date() > self.due_date


class EconomicSubstanceReport(models.Model):
    """Economic Substance Reporting for offshore entities."""
    
    BUSINESS_ACTIVITY_CHOICES = [
        ('BANKING', 'Banking Business'),
        ('INSURANCE', 'Insurance Business'),
        ('FUND_MANAGEMENT', 'Fund Management Business'),
        ('FINANCE_LEASING', 'Finance and Leasing Business'),
        ('HEADQUARTERS', 'Headquarters Business'),
        ('SHIPPING', 'Shipping Business'),
        ('HOLDING', 'Holding Company Business'),
        ('IP', 'Intellectual Property Business'),
        ('DISTRIBUTION', 'Distribution and Service Centre Business'),
        ('OTHER', 'Other Relevant Activity'),
        ('NONE', 'No Relevant Activity'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('SUBMITTED', 'Submitted'),
        ('REJECTED', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='economic_substance_reports')
    
    # Reporting period
    reporting_year = models.IntegerField(help_text="Year for this ES report")
    submission_deadline = models.DateField(help_text="Deadline for submission")
    submission_date = models.DateField(null=True, blank=True, help_text="Date when submitted")
    
    # Business activity
    business_activity = models.CharField(
        max_length=50,
        choices=BUSINESS_ACTIVITY_CHOICES,
        default='HOLDING'
    )
    activity_description = models.TextField(
        blank=True,
        help_text="Detailed description of business activities"
    )
    
    # Substance requirements (if relevant activity)
    has_adequate_employees = models.BooleanField(
        default=False,
        help_text="Does the entity have adequate number of qualified employees?"
    )
    num_employees = models.IntegerField(
        null=True,
        blank=True,
        help_text="Number of full-time employees"
    )
    
    has_adequate_premises = models.BooleanField(
        default=False,
        help_text="Does the entity have adequate physical premises?"
    )
    premises_address = models.TextField(
        blank=True,
        help_text="Physical premises address"
    )
    
    has_adequate_expenditure = models.BooleanField(
        default=False,
        help_text="Does the entity incur adequate operating expenditure?"
    )
    annual_expenditure = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual operating expenditure in local operations"
    )
    
    conducts_core_activities = models.BooleanField(
        default=False,
        help_text="Are core income-generating activities conducted in jurisdiction?"
    )
    core_activities_description = models.TextField(
        blank=True,
        help_text="Description of core activities conducted"
    )
    
    # Holding company specific (if applicable)
    is_pure_equity_holding = models.BooleanField(
        default=False,
        help_text="Is this a pure equity holding company?"
    )
    meets_reduced_substance = models.BooleanField(
        default=False,
        help_text="Meets reduced substance requirements (for holding companies)"
    )
    
    # Overall assessment
    meets_substance_requirements = models.BooleanField(
        default=False,
        help_text="Overall assessment: meets economic substance requirements"
    )
    
    # Status and documents
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Authority reference number"
    )
    pdf_file = models.FileField(
        upload_to='economic_substance/',
        null=True,
        blank=True,
        help_text="Generated PDF report"
    )
    
    # Metadata
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_es_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reporting_year']
        unique_together = ['company', 'reporting_year']
    
    def __str__(self):
        return f"{self.company.name} - ES Report {self.reporting_year}"


class JurisdictionFee(models.Model):
    """Track jurisdiction-specific fees (annual, renewal, etc.)."""
    
    FEE_TYPE_CHOICES = [
        ('ANNUAL_RENEWAL', 'Annual Renewal Fee'),
        ('GOVT_FEE', 'Government Fee'),
        ('REGISTERED_AGENT', 'Registered Agent Fee'),
        ('REGISTERED_OFFICE', 'Registered Office Fee'),
        ('ANNUAL_RETURN', 'Annual Return Filing Fee'),
        ('ES_REPORT', 'Economic Substance Report Fee'),
        ('AMENDMENT', 'Amendment/Change Fee'),
        ('APOSTILLE', 'Apostille Fee'),
        ('CERTIFICATE', 'Certificate Fee'),
        ('OTHER', 'Other Fee'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('WAIVED', 'Waived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jurisdiction_fees')
    
    # Fee details
    fee_type = models.CharField(max_length=30, choices=FEE_TYPE_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Dates
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Payment confirmation reference"
    )
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.company.name} - {self.get_fee_type_display()} ({self.due_date})"
    
    def is_overdue(self):
        """Check if the fee is overdue."""
        from django.utils import timezone
        if self.status == 'PAID':
            return False
        return timezone.now().date() > self.due_date


class ExchangeRate(models.Model):
    """Historical exchange rates for multi-currency support."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    from_currency = models.CharField(max_length=3, help_text="ISO 4217 currency code (e.g., USD)")
    to_currency = models.CharField(max_length=3, help_text="ISO 4217 currency code (e.g., EUR)")
    rate = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        help_text="Exchange rate (1 from_currency = rate to_currency)"
    )
    date = models.DateField(help_text="Date for this exchange rate")
    
    # Source tracking
    source = models.CharField(
        max_length=100,
        default='manual',
        help_text="Source of exchange rate (e.g., 'exchangerate-api', 'manual', 'central_bank')"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['from_currency', 'to_currency', 'date']
        indexes = [
            models.Index(fields=['from_currency', 'to_currency', 'date']),
        ]
    
    def __str__(self):
        return f"1 {self.from_currency} = {self.rate} {self.to_currency} ({self.date})"
    
    @classmethod
    def get_rate(cls, from_currency, to_currency, date):
        """Get exchange rate for a specific date."""
        if from_currency == to_currency:
            return 1.0
        
        try:
            rate = cls.objects.get(
                from_currency=from_currency,
                to_currency=to_currency,
                date=date
            )
            return rate.rate
        except cls.DoesNotExist:
            # Try to find the closest earlier date
            rate = cls.objects.filter(
                from_currency=from_currency,
                to_currency=to_currency,
                date__lte=date
            ).order_by('-date').first()
            
            if rate:
                return rate.rate
            
            # Try inverse rate
            try:
                inverse_rate = cls.objects.get(
                    from_currency=to_currency,
                    to_currency=from_currency,
                    date=date
                )
                return 1 / inverse_rate.rate
            except (cls.DoesNotExist, ZeroDivisionError):
                return None
    
    @classmethod
    def convert(cls, amount, from_currency, to_currency, date):
        """Convert amount from one currency to another."""
        rate = cls.get_rate(from_currency, to_currency, date)
        if rate is None:
            raise ValueError(f"No exchange rate found for {from_currency} to {to_currency} on {date}")
        return amount * rate


class CorporateServiceClient(models.Model):
    """Client record for corporate services providers."""
    
    CLIENT_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Individual'),
        ('COMPANY', 'Company'),
        ('TRUST', 'Trust'),
        ('FOUNDATION', 'Foundation'),
    ]
    
    STATUS_CHOICES = [
        ('PROSPECT', 'Prospect'),
        ('ACTIVE', 'Active Client'),
        ('INACTIVE', 'Inactive'),
        ('TERMINATED', 'Terminated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Client identification
    client_reference = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique client reference number"
    )
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES)
    client_name = models.CharField(max_length=255)
    
    # Contact details
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    country_of_residence = models.CharField(max_length=100, blank=True)
    
    # KYC/Due Diligence
    kyc_completed = models.BooleanField(default=False)
    kyc_completion_date = models.DateField(null=True, blank=True)
    kyc_review_date = models.DateField(
        null=True,
        blank=True,
        help_text="Next KYC review date (annual review)"
    )
    risk_rating = models.CharField(
        max_length=20,
        choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')],
        default='MEDIUM'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROSPECT')
    onboarding_date = models.DateField(null=True, blank=True)
    
    # Relationship manager
    relationship_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_clients'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['client_name']
    
    def __str__(self):
        return f"{self.client_reference} - {self.client_name}"
    
    def get_active_companies(self):
        """Get all active companies associated with this client."""
        return self.companies.filter(is_active=True)


# Add relation to Company model
Company.add_to_class(
    'corporate_client',
    models.ForeignKey(
        CorporateServiceClient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='companies',
        help_text='Corporate services client (if managed by a CSP)'
    )
)
