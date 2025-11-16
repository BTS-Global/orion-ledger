"""
Intelligent Account Mapping Service

This service provides smart account suggestions based on:
1. Historical transaction patterns
2. Keyword matching
3. Machine learning (future enhancement)
"""

from django.db.models import Count, Q
from collections import defaultdict
import re
from typing import List, Dict, Tuple

from .models import Transaction
from companies.models import ChartOfAccounts, Company


class AccountMapper:
    """
    Intelligent account mapping service that learns from historical data
    and provides smart suggestions for transaction categorization.
    """
    
    # Common keywords for account types
    KEYWORD_PATTERNS = {
        # Income accounts
        'INCOME': [
            r'\b(sale|sales|revenue|income|payment received|consulting|service)\b',
            r'\b(invoice|billing|client payment)\b',
        ],
        # Expense accounts
        'EXPENSE': [
            r'\b(rent|utilities|salary|salaries|wage|wages|payroll)\b',
            r'\b(office supplies|supplies|equipment|software|subscription)\b',
            r'\b(insurance|tax|taxes|fee|fees|interest)\b',
            r'\b(travel|meal|meals|entertainment|advertising|marketing)\b',
            r'\b(repair|maintenance|cleaning|security)\b',
        ],
        # Asset accounts
        'ASSET': [
            r'\b(equipment|computer|furniture|vehicle|building)\b',
            r'\b(inventory|stock|merchandise)\b',
        ],
        # Liability accounts
        'LIABILITY': [
            r'\b(loan|debt|payable|credit card|mortgage)\b',
        ],
    }
    
    # Specific account mappings
    SPECIFIC_ACCOUNT_KEYWORDS = {
        'office supplies': ['office supplies', 'staples', 'paper', 'pens', 'stationery'],
        'software': ['software', 'subscription', 'saas', 'adobe', 'microsoft'],
        'utilities': ['utilities', 'electricity', 'water', 'gas', 'internet', 'phone', 'comcast'],
        'rent': ['rent', 'lease', 'office rent'],
        'salaries': ['salary', 'salaries', 'wage', 'wages', 'payroll', 'employee'],
        'consulting': ['consulting', 'consultant', 'professional services'],
        'sales': ['sale', 'sales', 'product sale', 'customer'],
        'travel': ['travel', 'flight', 'hotel', 'airfare', 'uber', 'taxi'],
        'meals': ['meal', 'meals', 'restaurant', 'food', 'lunch', 'dinner'],
    }
    
    def __init__(self, company: Company):
        self.company = company
        self._cache = {}
    
    def suggest_account(self, description: str, amount: float = None) -> List[Dict]:
        """
        Suggest accounts for a transaction based on description and amount.
        
        Returns a list of suggestions with confidence scores:
        [
            {
                'account_id': '...',
                'account_code': '...',
                'account_name': '...',
                'confidence': 0.85,
                'reason': 'Historical pattern match'
            },
            ...
        ]
        """
        suggestions = []
        
        # 1. Check historical patterns
        historical_suggestions = self._get_historical_suggestions(description)
        suggestions.extend(historical_suggestions)
        
        # 2. Check keyword patterns
        keyword_suggestions = self._get_keyword_suggestions(description, amount)
        suggestions.extend(keyword_suggestions)
        
        # 3. Merge and rank suggestions
        merged_suggestions = self._merge_and_rank_suggestions(suggestions)
        
        return merged_suggestions[:5]  # Return top 5 suggestions
    
    def _get_historical_suggestions(self, description: str) -> List[Dict]:
        """
        Find accounts that were used for similar transactions in the past.
        """
        suggestions = []
        
        # Normalize description
        desc_lower = description.lower().strip()
        
        # Find similar transactions (exact match first)
        similar_transactions = Transaction.objects.filter(
            company=self.company,
            description__iexact=desc_lower,
            account__isnull=False
        ).values('account', 'account__account_code', 'account__account_name').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        for trans in similar_transactions:
            suggestions.append({
                'account_id': str(trans['account']),
                'account_code': trans['account__account_code'],
                'account_name': trans['account__account_name'],
                'confidence': 0.9,  # High confidence for exact match
                'reason': f'Used {trans["count"]} time(s) for similar transactions'
            })
        
        # If no exact match, try partial match
        if not suggestions:
            # Extract key words from description (words with 4+ characters)
            keywords = [word for word in desc_lower.split() if len(word) >= 4]
            
            if keywords:
                # Build Q object for OR query
                q_objects = Q()
                for keyword in keywords[:3]:  # Use top 3 keywords
                    q_objects |= Q(description__icontains=keyword)
                
                similar_transactions = Transaction.objects.filter(
                    q_objects,
                    company=self.company,
                    account__isnull=False
                ).values('account', 'account__account_code', 'account__account_name').annotate(
                    count=Count('id')
                ).order_by('-count')[:2]
                
                for trans in similar_transactions:
                    suggestions.append({
                        'account_id': str(trans['account']),
                        'account_code': trans['account__account_code'],
                        'account_name': trans['account__account_name'],
                        'confidence': 0.6,  # Lower confidence for partial match
                        'reason': f'Similar to {trans["count"]} previous transaction(s)'
                    })
        
        return suggestions
    
    def _get_keyword_suggestions(self, description: str, amount: float = None) -> List[Dict]:
        """
        Suggest accounts based on keyword matching.
        """
        suggestions = []
        desc_lower = description.lower()
        
        # First, try specific account keyword matching
        for account_type, keywords in self.SPECIFIC_ACCOUNT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    # Find account with matching name or description
                    accounts = ChartOfAccounts.objects.filter(
                        company=self.company,
                        is_active=True
                    ).filter(
                        Q(account_name__icontains=account_type) |
                        Q(description__icontains=account_type)
                    )[:1]
                    
                    for account in accounts:
                        suggestions.append({
                            'account_id': str(account.id),
                            'account_code': account.account_code,
                            'account_name': account.account_name,
                            'confidence': 0.7,
                            'reason': f'Keyword match: "{keyword}"'
                        })
                        break  # Only one suggestion per keyword match
        
        # Then, try general account type matching
        if not suggestions:
            for account_type, patterns in self.KEYWORD_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, desc_lower, re.IGNORECASE):
                        # Find accounts of this type
                        accounts = ChartOfAccounts.objects.filter(
                            company=self.company,
                            account_type=account_type,
                            is_active=True
                        )[:2]
                        
                        for account in accounts:
                            suggestions.append({
                                'account_id': str(account.id),
                                'account_code': account.account_code,
                                'account_name': account.account_name,
                                'confidence': 0.5,
                                'reason': f'Account type match: {account_type}'
                            })
        
        return suggestions
    
    def _merge_and_rank_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """
        Merge duplicate suggestions and rank by confidence.
        """
        # Group by account_id
        merged = {}
        for suggestion in suggestions:
            account_id = suggestion['account_id']
            if account_id in merged:
                # Keep the one with higher confidence
                if suggestion['confidence'] > merged[account_id]['confidence']:
                    merged[account_id] = suggestion
            else:
                merged[account_id] = suggestion
        
        # Sort by confidence (descending)
        ranked = sorted(merged.values(), key=lambda x: x['confidence'], reverse=True)
        
        return ranked
    
    def learn_from_transaction(self, transaction: Transaction):
        """
        Learn from a validated transaction to improve future suggestions.
        This method can be called after a transaction is imported and validated.
        """
        # For now, this is a placeholder for future ML implementation
        # The historical matching already learns from past transactions
        pass
    
    def get_account_statistics(self) -> Dict:
        """
        Get statistics about account usage for the company.
        """
        stats = {
            'total_transactions': Transaction.objects.filter(company=self.company).count(),
            'transactions_with_accounts': Transaction.objects.filter(
                company=self.company,
                account__isnull=False
            ).count(),
            'most_used_accounts': []
        }
        
        # Get most used accounts
        most_used = Transaction.objects.filter(
            company=self.company,
            account__isnull=False
        ).values(
            'account',
            'account__account_code',
            'account__account_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        stats['most_used_accounts'] = [
            {
                'account_id': str(item['account']),
                'account_code': item['account__account_code'],
                'account_name': item['account__account_name'],
                'usage_count': item['count']
            }
            for item in most_used
        ]
        
        return stats

