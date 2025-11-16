"""
Custom exceptions for accounting operations.
"""


class AccountingException(Exception):
    """Base exception for accounting operations."""
    pass


class FutureOperationError(AccountingException):
    """Raised when trying to perform an operation in the future."""
    pass


class RetroactiveOperationError(AccountingException):
    """Raised when trying to perform a retroactive operation after a balance snapshot or closing."""
    pass


class InconsistentDataError(AccountingException):
    """Raised when data inconsistency is detected."""
    pass


class InsufficientBalanceError(AccountingException):
    """Raised when there's insufficient balance for an operation."""
    pass


class ArchivedCompanyError(AccountingException):
    """Raised when trying to perform operations on an archived company."""
    pass


class ClosedPeriodError(AccountingException):
    """Raised when trying to modify a closed accounting period."""
    pass

