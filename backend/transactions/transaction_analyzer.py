"""
Advanced AI service for transaction analysis and categorization.
"""
import re
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Q
from transactions.models import Transaction
from companies.models import ChartOfAccounts


class TransactionAnalyzer:
    """Advanced AI-powered transaction analysis."""
    
    # Common transaction patterns
    PATTERNS = {
        'rent': {
            'keywords': ['rent', 'rental', 'lease', 'property'],
            'suggested_account': '5240',  # Rent Expense
            'frequency': 'monthly',
        },
        'utilities': {
            'keywords': ['electric', 'gas', 'water', 'utility', 'power', 'energy'],
            'suggested_account': '5250',  # Utilities
            'frequency': 'monthly',
        },
        'payroll': {
            'keywords': ['salary', 'wage', 'payroll', 'compensation'],
            'suggested_account': '5210',  # Salaries and Wages
            'frequency': 'biweekly',
        },
        'insurance': {
            'keywords': ['insurance', 'policy', 'premium'],
            'suggested_account': '5260',  # Insurance
            'frequency': 'monthly',
        },
        'advertising': {
            'keywords': ['ads', 'advertising', 'marketing', 'promotion', 'google ads', 'facebook ads'],
            'suggested_account': '5290',  # Marketing and Advertising
            'frequency': 'variable',
        },
        'software': {
            'keywords': ['software', 'saas', 'subscription', 'hosting', 'cloud'],
            'suggested_account': '5330',  # Technology and Software
            'frequency': 'monthly',
        },
        'office_supplies': {
            'keywords': ['supplies', 'stationery', 'paper', 'printer'],
            'suggested_account': '5310',  # Office Supplies
            'frequency': 'variable',
        },
        'travel': {
            'keywords': ['travel', 'flight', 'hotel', 'airfare', 'airline'],
            'suggested_account': '5320',  # Travel and Entertainment
            'frequency': 'variable',
        },
        'bank_fees': {
            'keywords': ['bank fee', 'service charge', 'transaction fee', 'atm fee'],
            'suggested_account': '5420',  # Bank Fees
            'frequency': 'variable',
        },
        'interest': {
            'keywords': ['interest income', 'interest earned'],
            'suggested_account': '4910',  # Interest Income
            'frequency': 'monthly',
        },
        'sales': {
            'keywords': ['sale', 'revenue', 'invoice', 'payment received'],
            'suggested_account': '4110',  # Sales Revenue
            'frequency': 'variable',
        },
    }
    
    def __init__(self, company):
        self.company = company
    
    def analyze_transaction(self, description: str, amount: Decimal, 
                          transaction_type: str = 'DEBIT') -> Dict:
        """
        Perform comprehensive analysis of a transaction.
        
        Returns:
            dict: Analysis results with confidence scores and suggestions
        """
        description_lower = description.lower()
        
        # Pattern matching
        matched_patterns = []
        for pattern_name, pattern_data in self.PATTERNS.items():
            for keyword in pattern_data['keywords']:
                if keyword in description_lower:
                    matched_patterns.append({
                        'pattern': pattern_name,
                        'account': pattern_data['suggested_account'],
                        'frequency': pattern_data['frequency'],
                        'confidence': self._calculate_confidence(keyword, description_lower)
                    })
                    break
        
        # Get account suggestions
        suggestions = []
        if matched_patterns:
            # Sort by confidence
            matched_patterns.sort(key=lambda x: x['confidence'], reverse=True)
            
            for pattern in matched_patterns[:3]:  # Top 3 matches
                try:
                    account = ChartOfAccounts.objects.get(
                        company=self.company,
                        account_code=pattern['account']
                    )
                    suggestions.append({
                        'account_id': str(account.id),
                        'account_code': account.account_code,
                        'account_name': account.account_name,
                        'confidence': pattern['confidence'],
                        'pattern': pattern['pattern'],
                        'frequency': pattern['frequency']
                    })
                except ChartOfAccounts.DoesNotExist:
                    pass
        
        # Analyze amount patterns
        amount_analysis = self._analyze_amount(amount, description)
        
        # Check for recurring transactions
        recurring_analysis = self._check_recurring(description, amount)
        
        return {
            'description': description,
            'amount': float(amount),
            'type': transaction_type,
            'suggestions': suggestions,
            'amount_analysis': amount_analysis,
            'recurring_analysis': recurring_analysis,
            'matched_patterns': [p['pattern'] for p in matched_patterns],
            'confidence_score': matched_patterns[0]['confidence'] if matched_patterns else 0.0
        }
    
    def _calculate_confidence(self, keyword: str, description: str) -> float:
        """Calculate confidence score based on keyword match quality."""
        # Exact match at start
        if description.startswith(keyword):
            return 0.95
        
        # Exact match with word boundary
        if re.search(r'\b' + re.escape(keyword) + r'\b', description):
            return 0.85
        
        # Partial match
        if keyword in description:
            return 0.70
        
        return 0.50
    
    def _analyze_amount(self, amount: Decimal, description: str) -> Dict:
        """Analyze amount for patterns and anomalies."""
        amount_float = float(amount)
        
        analysis = {
            'is_round_number': amount_float == int(amount_float),
            'is_large': amount_float > 10000,
            'is_small': amount_float < 10,
            'magnitude': 'small' if amount_float < 100 else 'medium' if amount_float < 1000 else 'large'
        }
        
        # Check for common amount patterns
        if amount_float == int(amount_float) and amount_float > 100:
            analysis['likely_recurring'] = True
        else:
            analysis['likely_recurring'] = False
        
        return analysis
    
    def _check_recurring(self, description: str, amount: Decimal) -> Dict:
        """Check if this might be a recurring transaction."""
        # Look for similar transactions in the past
        similar_transactions = Transaction.objects.filter(
            company=self.company,
            description__icontains=description[:20]  # First 20 chars
        ).order_by('-date')[:5]
        
        if similar_transactions.count() >= 2:
            # Check time intervals
            dates = [t.date for t in similar_transactions]
            if len(dates) >= 2:
                intervals = []
                for i in range(len(dates) - 1):
                    interval = (dates[i] - dates[i + 1]).days
                    intervals.append(interval)
                
                avg_interval = sum(intervals) / len(intervals) if intervals else 0
                
                # Determine frequency
                frequency = 'unknown'
                if 25 <= avg_interval <= 35:
                    frequency = 'monthly'
                elif 12 <= avg_interval <= 16:
                    frequency = 'biweekly'
                elif 6 <= avg_interval <= 8:
                    frequency = 'weekly'
                elif 85 <= avg_interval <= 95:
                    frequency = 'quarterly'
                
                return {
                    'is_recurring': True,
                    'occurrences': similar_transactions.count(),
                    'frequency': frequency,
                    'average_interval_days': int(avg_interval)
                }
        
        return {
            'is_recurring': False,
            'occurrences': 0,
            'frequency': 'unknown',
            'average_interval_days': 0
        }
    
    def batch_analyze(self, transactions: List[Transaction]) -> Dict:
        """
        Analyze multiple transactions and provide insights.
        
        Args:
            transactions: List of Transaction objects
            
        Returns:
            dict: Batch analysis results
        """
        total = len(transactions)
        analyzed = 0
        high_confidence = 0
        medium_confidence = 0
        low_confidence = 0
        
        category_distribution = {}
        
        for transaction in transactions:
            result = self.analyze_transaction(
                transaction.description,
                transaction.amount,
                transaction.type
            )
            analyzed += 1
            
            confidence = result['confidence_score']
            if confidence >= 0.80:
                high_confidence += 1
            elif confidence >= 0.60:
                medium_confidence += 1
            else:
                low_confidence += 1
            
            # Track category distribution
            if result['suggestions']:
                pattern = result['matched_patterns'][0] if result['matched_patterns'] else 'unknown'
                category_distribution[pattern] = category_distribution.get(pattern, 0) + 1
        
        return {
            'total_transactions': total,
            'analyzed': analyzed,
            'confidence_distribution': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            },
            'category_distribution': category_distribution,
            'accuracy_rate': (high_confidence / total * 100) if total > 0 else 0
        }
    
    def suggest_account_improvements(self) -> List[Dict]:
        """
        Analyze transaction history and suggest account structure improvements.
        
        Returns:
            list: List of suggestions for improving chart of accounts
        """
        suggestions = []
        
        # Find unvalidated transactions
        unvalidated = Transaction.objects.filter(
            company=self.company,
            is_validated=False
        ).count()
        
        if unvalidated > 10:
            suggestions.append({
                'type': 'validation',
                'priority': 'high',
                'message': f'You have {unvalidated} unvalidated transactions. Consider validating them to improve accuracy.'
            })
        
        # Check for missing common accounts
        existing_codes = set(
            ChartOfAccounts.objects.filter(company=self.company)
            .values_list('account_code', flat=True)
        )
        
        common_accounts = ['5240', '5250', '5210', '5260', '5290', '5330']
        missing = [code for code in common_accounts if code not in existing_codes]
        
        if missing:
            suggestions.append({
                'type': 'missing_accounts',
                'priority': 'medium',
                'message': f'Consider adding {len(missing)} commonly used accounts to your chart.',
                'missing_codes': missing
            })
        
        # Check account usage
        account_usage = Transaction.objects.filter(
            company=self.company,
            is_validated=True,
            account__isnull=False
        ).values('account').annotate(count=Count('id')).order_by('-count')
        
        if account_usage.count() > 0:
            top_account = account_usage.first()
            if top_account['count'] > 50:
                suggestions.append({
                    'type': 'account_usage',
                    'priority': 'low',
                    'message': 'One account is being used very frequently. Consider creating sub-accounts for better tracking.'
                })
        
        return suggestions
