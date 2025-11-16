"""
Caching service for improving performance of frequent queries.
"""
from django.core.cache import cache
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal


class AccountingCache:
    """
    Cache manager for accounting data to improve performance.
    """
    
    CACHE_TIMEOUT = {
        'balance': 300,  # 5 minutes
        'statistics': 600,  # 10 minutes
        'hierarchy': 900,  # 15 minutes
        'reports': 1800,  # 30 minutes
    }
    
    @classmethod
    def _get_key(cls, prefix: str, company_id: str, **kwargs) -> str:
        """Generate cache key."""
        key_parts = [prefix, str(company_id)]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    @classmethod
    def get_account_balance(cls, account_id: str, company_id: str) -> Optional[Decimal]:
        """Get cached account balance."""
        key = cls._get_key('account_balance', company_id, account=account_id)
        return cache.get(key)
    
    @classmethod
    def set_account_balance(cls, account_id: str, company_id: str, balance: Decimal):
        """Cache account balance."""
        key = cls._get_key('account_balance', company_id, account=account_id)
        cache.set(key, balance, cls.CACHE_TIMEOUT['balance'])
    
    @classmethod
    def invalidate_account_balance(cls, account_id: str, company_id: str):
        """Invalidate account balance cache."""
        key = cls._get_key('account_balance', company_id, account=account_id)
        cache.delete(key)
    
    @classmethod
    def get_company_statistics(cls, company_id: str) -> Optional[Dict]:
        """Get cached company statistics."""
        key = cls._get_key('company_stats', company_id)
        return cache.get(key)
    
    @classmethod
    def set_company_statistics(cls, company_id: str, stats: Dict):
        """Cache company statistics."""
        key = cls._get_key('company_stats', company_id)
        cache.set(key, stats, cls.CACHE_TIMEOUT['statistics'])
    
    @classmethod
    def invalidate_company_statistics(cls, company_id: str):
        """Invalidate company statistics cache."""
        key = cls._get_key('company_stats', company_id)
        cache.delete(key)
    
    @classmethod
    def get_account_hierarchy(cls, company_id: str) -> Optional[List]:
        """Get cached account hierarchy."""
        key = cls._get_key('account_hierarchy', company_id)
        return cache.get(key)
    
    @classmethod
    def set_account_hierarchy(cls, company_id: str, hierarchy: List):
        """Cache account hierarchy."""
        key = cls._get_key('account_hierarchy', company_id)
        cache.set(key, hierarchy, cls.CACHE_TIMEOUT['hierarchy'])
    
    @classmethod
    def invalidate_account_hierarchy(cls, company_id: str):
        """Invalidate account hierarchy cache."""
        key = cls._get_key('account_hierarchy', company_id)
        cache.delete(key)
    
    @classmethod
    def get_trial_balance(cls, company_id: str, start_date: str, end_date: str) -> Optional[Dict]:
        """Get cached trial balance."""
        key = cls._get_key('trial_balance', company_id, 
                          start=start_date, end=end_date)
        return cache.get(key)
    
    @classmethod
    def set_trial_balance(cls, company_id: str, start_date: str, 
                         end_date: str, data: Dict):
        """Cache trial balance."""
        key = cls._get_key('trial_balance', company_id, 
                          start=start_date, end=end_date)
        cache.set(key, data, cls.CACHE_TIMEOUT['reports'])
    
    @classmethod
    def invalidate_trial_balance(cls, company_id: str):
        """Invalidate all trial balance caches for a company."""
        # Note: This is a simple implementation. For production, 
        # consider using cache key patterns or redis SCAN
        cache.delete_pattern(f"trial_balance:{company_id}:*")
    
    @classmethod
    def invalidate_all_company_caches(cls, company_id: str):
        """Invalidate all caches for a company."""
        cls.invalidate_company_statistics(company_id)
        cls.invalidate_account_hierarchy(company_id)
        cls.invalidate_trial_balance(company_id)
        # Note: Individual account balances are not invalidated here
        # They should be invalidated when specific accounts are modified


class QueryOptimizer:
    """
    Query optimization utilities for common accounting queries.
    """
    
    @staticmethod
    def get_account_with_related(account_id: str):
        """
        Get account with all related data in a single query.
        Uses select_related and prefetch_related for optimization.
        """
        from companies.models import ChartOfAccounts
        
        return ChartOfAccounts.objects.select_related(
            'company',
            'parent_account'
        ).prefetch_related(
            'child_accounts',
            'transactions'
        ).get(id=account_id)
    
    @staticmethod
    def get_transactions_with_related(company_id: str, **filters):
        """
        Get transactions with all related data optimized.
        """
        from transactions.models import Transaction
        
        queryset = Transaction.objects.select_related(
            'company',
            'account',
            'document',
            'validated_by'
        ).filter(company_id=company_id)
        
        # Apply additional filters
        for key, value in filters.items():
            queryset = queryset.filter(**{key: value})
        
        return queryset
    
    @staticmethod
    def get_journal_entries_with_lines(company_id: str, **filters):
        """
        Get journal entries with lines in optimized way.
        """
        from transactions.models import JournalEntry
        
        queryset = JournalEntry.objects.select_related(
            'company',
            'transaction'
        ).prefetch_related(
            'lines',
            'lines__account'
        ).filter(company_id=company_id)
        
        # Apply additional filters
        for key, value in filters.items():
            queryset = queryset.filter(**{key: value})
        
        return queryset
    
    @staticmethod
    def bulk_create_transactions(transactions: List) -> int:
        """
        Bulk create transactions for better performance.
        Returns number of created transactions.
        """
        from transactions.models import Transaction
        
        created = Transaction.objects.bulk_create(
            transactions,
            batch_size=100,
            ignore_conflicts=False
        )
        return len(created)
    
    @staticmethod
    def bulk_update_transactions(transactions: List, fields: List[str]) -> int:
        """
        Bulk update transactions for better performance.
        Returns number of updated transactions.
        """
        from transactions.models import Transaction
        
        updated = Transaction.objects.bulk_update(
            transactions,
            fields,
            batch_size=100
        )
        return updated


class PerformanceMonitor:
    """
    Monitor and log slow queries and performance issues.
    """
    
    SLOW_QUERY_THRESHOLD = 1.0  # seconds
    
    @classmethod
    def log_slow_query(cls, query_name: str, execution_time: float, 
                      details: Optional[Dict] = None):
        """Log slow query for analysis."""
        if execution_time > cls.SLOW_QUERY_THRESHOLD:
            print(f"[SLOW QUERY] {query_name}: {execution_time:.2f}s")
            if details:
                print(f"  Details: {details}")
    
    @classmethod
    def measure_query(cls, query_name: str):
        """Decorator to measure query execution time."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                import time
                start = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start
                cls.log_slow_query(query_name, execution_time)
                return result
            return wrapper
        return decorator
