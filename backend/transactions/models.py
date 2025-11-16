from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, F
from django.utils import timezone
from companies.models import Company, ChartOfAccounts
from documents.models import Document
import uuid

# Import manager (will be defined after model)
from transactions.balance_manager import JournalEntryBalanceManager


class Transaction(models.Model):
    """Model for financial transactions."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Account assignment
    account = models.ForeignKey(
        ChartOfAccounts, 
        on_delete=models.PROTECT, 
        related_name='transactions',
        null=True,
        blank=True
    )
    
    # Source document
    document = models.ForeignKey(
        Document, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL, 
        related_name='transactions'
    )
    
    # Validation status
    is_validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        User, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL, 
        related_name='validated_transactions'
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    
    # AI-suggested category
    suggested_category = models.CharField(max_length=100, blank=True)
    confidence_score = models.FloatField(null=True, blank=True, help_text="AI confidence score (0-1)")
    
    # RAG and ML fields
    vendor = models.CharField(max_length=255, blank=True, help_text="Vendor/merchant name")
    category = models.CharField(max_length=100, blank=True, help_text="Transaction category")
    embedding = models.JSONField(null=True, blank=True, help_text="Vector embedding for RAG")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['company', 'is_validated']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gte=0),
                name='transaction_amount_gte_zero'
            ),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.description[:50]} - ${self.amount}"


class JournalEntry(models.Model):
    """Model for double-entry journal entries."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='journal_entries')
    date = models.DateField()
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    
    # Link to source transaction if applicable
    transaction = models.ForeignKey(
        Transaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='journal_entries'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Journal Entries"
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['company', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.description[:50]}"
    
    @property
    def is_balanced(self):
        """Check if debits equal credits."""
        total_debit = sum(line.debit for line in self.lines.all())
        total_credit = sum(line.credit for line in self.lines.all())
        return abs(total_debit - total_credit) < 0.01  # Allow for rounding errors


class JournalEntryLine(models.Model):
    """Individual lines in a journal entry (double-entry bookkeeping)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal_entry = models.ForeignKey(
        JournalEntry, 
        on_delete=models.CASCADE, 
        related_name='lines'
    )
    account = models.ForeignKey(
        ChartOfAccounts, 
        on_delete=models.PROTECT, 
        related_name='journal_lines'
    )
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
        constraints = [
            models.CheckConstraint(
                condition=Q(debit__gte=0),
                name='journal_line_debit_gte_zero'
            ),
            models.CheckConstraint(
                condition=Q(credit__gte=0),
                name='journal_line_credit_gte_zero'
            ),
            models.CheckConstraint(
                condition=~(Q(debit__gt=0) & Q(credit__gt=0)),
                name='journal_line_debit_or_credit_not_both'
            ),
        ]
    
    def __str__(self):
        return f"{self.account.account_code} - D:{self.debit} C:{self.credit}"




class JournalEntryBalance(models.Model):
    """
    Pre-calculated balance snapshots for performance optimization.
    
    This model stores balance snapshots at specific points in time to avoid
    recalculating balances from all historical journal entries. This dramatically
    improves performance when there are many entries.
    
    Similar to LedgerBookBalance in Cotizador system.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='balance_snapshots'
    )
    account = models.ForeignKey(
        ChartOfAccounts, 
        on_delete=models.PROTECT, 
        related_name='balance_snapshots'
    )
    timestamp = models.DateTimeField(
        validators=[MaxValueValidator(timezone.now)],
        help_text="Snapshot timestamp (cannot be in the future)"
    )
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Pre-calculated balance at this timestamp"
    )
    last_checked_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Last time this balance was verified"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Custom manager
    objects = JournalEntryBalanceManager()
    
    class Meta:
        verbose_name_plural = "Journal Entry Balances"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['company', 'account', '-timestamp']),
            models.Index(fields=['company', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'account', 'timestamp'],
                name='unique_balance_snapshot'
            ),
            models.CheckConstraint(
                condition=Q(timestamp__lte=timezone.now()),
                name='balance_timestamp_not_future'
            ),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.account.account_name} - {self.timestamp} - ${self.balance}"


class AccountingClosing(models.Model):
    """
    Accounting period closings.
    
    Represents the closing of an accounting period. Once closed, no retroactive
    entries can be made before the closing date.
    """
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('AUDITED', 'Audited'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='closings'
    )
    closing_date = models.DateField(
        help_text="Last date of the closed period"
    )
    period_name = models.CharField(
        max_length=100,
        help_text="e.g., 'Q1 2025', 'FY 2024'"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    closed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='closings_performed'
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    audited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='closings_audited'
    )
    audited_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Accounting Closings"
        ordering = ['-closing_date']
        indexes = [
            models.Index(fields=['company', '-closing_date']),
            models.Index(fields=['company', 'status']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(closing_date__lte=timezone.now().date()),
                name='closing_date_not_future'
            ),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.period_name} - {self.status}"

