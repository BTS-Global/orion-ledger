"""
Balance Manager for optimized balance calculations.

Inspired by Cotizador's LedgerBookBalanceManager.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone

from core.exceptions import FutureOperationError, RetroactiveOperationError


class JournalEntryBalanceManager(models.Manager):
    """
    Manager for JournalEntryBalance with optimized balance calculation methods.
    """
    
    def create_balance(self, company, account, timestamp):
        """
        Create a balance snapshot for a specific account at a specific timestamp.
        
        Args:
            company: Company object
            account: ChartOfAccounts object
            timestamp: DateTime for the snapshot
            
        Returns:
            JournalEntryBalance object
            
        Raises:
            FutureOperationError: If timestamp is in the future
            RetroactiveOperationError: If there's already a newer balance
        """
        if timestamp > timezone.now():
            raise FutureOperationError("Cannot create balance snapshot in the future")
        
        if self.filter(company=company, account=account, timestamp__gte=timestamp).exists():
            raise RetroactiveOperationError("There's already a newer balance snapshot")
        
        # Calculate balance at this timestamp
        balance = self.calculate_balance(company, account, timestamp)
        
        return self.create(
            company=company,
            account=account,
            timestamp=timestamp,
            balance=balance
        )
    
    def save_balances(self, company, timestamp):
        """
        Save balance snapshots for all accounts of a company at a specific timestamp.
        
        Args:
            company: Company object
            timestamp: DateTime for the snapshots
        """
        from companies.models import ChartOfAccounts
        from transactions.models import JournalEntryLine
        
        accounts = ChartOfAccounts.objects.filter(company=company, is_active=True)
        
        for account in accounts:
            # Check if there are entries for this account
            entries_exist = JournalEntryLine.objects.filter(
                Q(account=account) & 
                Q(journal_entry__company=company)
            ).exists()
            
            if not entries_exist:
                continue
            
            # Check if we need to create a new snapshot
            try:
                last_snapshot = self.filter(
                    company=company, 
                    account=account
                ).latest('timestamp')
                
                # Only create if there are new entries after last snapshot
                new_entries = JournalEntryLine.objects.filter(
                    Q(account=account) &
                    Q(journal_entry__company=company) &
                    Q(journal_entry__date__gt=last_snapshot.timestamp.date())
                ).exists()
                
                if not new_entries:
                    continue
                    
            except self.model.DoesNotExist:
                pass  # No previous snapshot, create one
            
            # Create the snapshot
            try:
                self.create_balance(company, account, timestamp)
            except (FutureOperationError, RetroactiveOperationError):
                continue  # Skip if validation fails
    
    def calculate_balance(self, company, account, timestamp=None):
        """
        Calculate the balance of an account at a specific timestamp.
        
        Uses the latest balance snapshot as a starting point for performance.
        
        Args:
            company: Company object
            account: ChartOfAccounts object
            timestamp: DateTime (None = current time)
            
        Returns:
            Decimal: Account balance (positive = credit, negative = debit)
        """
        from transactions.models import JournalEntry, JournalEntryLine
        
        if timestamp is None:
            timestamp = timezone.now()
        
        # Try to find the latest balance snapshot before this timestamp
        try:
            latest_snapshot = self.filter(
                company=company,
                account=account,
                timestamp__lte=timestamp
            ).latest('timestamp')
            
            # Start from the snapshot balance
            balance = latest_snapshot.balance
            cutoff_date = latest_snapshot.timestamp
            
        except self.model.DoesNotExist:
            # No snapshot found, calculate from the beginning
            balance = Decimal('0.00')
            cutoff_date = None
        
        # Get all journal entry lines for this account after the cutoff
        lines_query = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__company=company
        )
        
        if cutoff_date:
            lines_query = lines_query.filter(
                journal_entry__date__gt=cutoff_date.date()
            )
        
        # Filter by timestamp if provided
        if timestamp:
            lines_query = lines_query.filter(
                journal_entry__date__lte=timestamp.date()
            )
        
        # Calculate debits and credits
        aggregates = lines_query.aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        total_debit = aggregates['total_debit'] or Decimal('0.00')
        total_credit = aggregates['total_credit'] or Decimal('0.00')
        
        # Update balance (credit increases, debit decreases)
        balance += (total_credit - total_debit)
        
        return balance
    
    def calculate_balances(self, company, accounts, timestamp=None):
        """
        Calculate aggregated balance for multiple accounts.
        
        Args:
            company: Company object
            accounts: List of ChartOfAccounts objects
            timestamp: DateTime (None = current time)
            
        Returns:
            Decimal: Aggregated balance
        """
        total_balance = Decimal('0.00')
        
        for account in accounts:
            balance = self.calculate_balance(company, account, timestamp)
            total_balance += balance
        
        return total_balance
    
    def credits_debits(self, company, accounts, start_date, end_date=None):
        """
        Calculate total credits and debits for accounts in a date range.
        
        Args:
            company: Company object
            accounts: List of ChartOfAccounts objects
            start_date: Start date
            end_date: End date (None = today)
            
        Returns:
            Tuple: (total_credits, total_debits)
        """
        from transactions.models import JournalEntryLine
        
        if end_date is None:
            end_date = timezone.now().date()
        
        lines_query = JournalEntryLine.objects.filter(
            account__in=accounts,
            journal_entry__company=company,
            journal_entry__date__gte=start_date,
            journal_entry__date__lte=end_date
        )
        
        aggregates = lines_query.aggregate(
            total_credit=Sum('credit'),
            total_debit=Sum('debit')
        )
        
        total_credit = aggregates['total_credit'] or Decimal('0.00')
        total_debit = aggregates['total_debit'] or Decimal('0.00')
        
        return (total_credit, total_debit)

