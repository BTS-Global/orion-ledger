"""
Validators for accounting operations.
"""
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.exceptions import (
    FutureOperationError,
    ArchivedCompanyError,
    RetroactiveOperationError,
)


def validate_timestamp_not_in_future(timestamp, error_message=None):
    """
    Validate that a timestamp is not in the future.
    
    Args:
        timestamp: DateTime to validate
        error_message: Custom error message
        
    Raises:
        FutureOperationError: If timestamp is in the future
    """
    if timestamp > timezone.now():
        msg = error_message or _("Cannot create entry in the future")
        raise FutureOperationError(msg)


def validate_company_not_archived(company, error_message=None):
    """
    Validate that a company is not archived.
    
    Args:
        company: Company object to validate
        error_message: Custom error message
        
    Raises:
        ArchivedCompanyError: If company is archived
    """
    if hasattr(company, 'is_archived') and company.is_archived:
        msg = error_message or _("Cannot perform operation on archived company")
        raise ArchivedCompanyError(msg)


def validate_timestamp_after_last_closing(company, timestamp, error_message=None):
    """
    Validate that timestamp is after the last accounting closing.
    
    Args:
        company: Company object
        timestamp: DateTime to validate
        error_message: Custom error message
        
    Raises:
        RetroactiveOperationError: If timestamp is before last closing
    """
    # Import here to avoid circular dependency
    from transactions.models import AccountingClosing
    
    last_closing = AccountingClosing.objects.filter(
        company=company,
        status='CLOSED'
    ).order_by('-closing_date').first()
    
    if last_closing and timestamp.date() <= last_closing.closing_date:
        msg = error_message or _(
            f"Cannot create entry before last closing date ({last_closing.closing_date})"
        )
        raise RetroactiveOperationError(msg)


def validate_timestamp_after_last_balance(company, account, timestamp, error_message=None):
    """
    Validate that timestamp is after the last balance snapshot.
    
    Args:
        company: Company object
        account: Account object
        timestamp: DateTime to validate
        error_message: Custom error message
        
    Raises:
        RetroactiveOperationError: If timestamp is before last balance
    """
    # Import here to avoid circular dependency
    from transactions.models import JournalEntryBalance
    
    last_balance = JournalEntryBalance.objects.filter(
        company=company,
        account=account
    ).order_by('-timestamp').first()
    
    if last_balance and timestamp <= last_balance.timestamp:
        msg = error_message or _(
            f"Cannot create entry before last balance snapshot ({last_balance.timestamp})"
        )
        raise RetroactiveOperationError(msg)

