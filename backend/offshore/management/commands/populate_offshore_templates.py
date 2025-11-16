"""
Management command to populate offshore templates and sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from companies.models import Company, ChartOfAccounts
from offshore.models import ExchangeRate
from datetime import date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populates offshore jurisdiction templates and sample exchange rates'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting offshore templates population...'))
        
        # Create sample exchange rates
        self.create_exchange_rates()
        
        self.stdout.write(self.style.SUCCESS('Offshore templates population complete!'))
    
    def create_exchange_rates(self):
        """Create sample exchange rates for common currencies."""
        self.stdout.write('Creating exchange rates...')
        
        # Sample exchange rates for last 30 days
        today = date.today()
        
        # USD to major currencies
        rates = [
            ('USD', 'EUR', Decimal('0.92')),
            ('USD', 'GBP', Decimal('0.79')),
            ('USD', 'BRL', Decimal('5.10')),
            ('USD', 'CAD', Decimal('1.36')),
            ('USD', 'CHF', Decimal('0.88')),
            ('USD', 'AUD', Decimal('1.53')),
            ('USD', 'SGD', Decimal('1.35')),
            ('USD', 'HKD', Decimal('7.80')),
            ('EUR', 'USD', Decimal('1.09')),
            ('GBP', 'USD', Decimal('1.27')),
            ('BRL', 'USD', Decimal('0.20')),
        ]
        
        # Create rates for last 30 days
        created_count = 0
        for i in range(30):
            rate_date = today - timedelta(days=i)
            
            for from_curr, to_curr, base_rate in rates:
                # Add small random variation (±2%)
                variation = Decimal('0.98') + (Decimal('0.04') * Decimal(i % 5) / Decimal('10'))
                rate_value = base_rate * variation
                
                ExchangeRate.objects.get_or_create(
                    from_currency=from_curr,
                    to_currency=to_curr,
                    date=rate_date,
                    defaults={
                        'rate': rate_value,
                        'source': 'sample_data'
                    }
                )
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} exchange rate records'))
    
    def create_offshore_coa_template(self, company, jurisdiction):
        """Create a Chart of Accounts template for offshore entities."""
        
        # Simplified offshore COA
        accounts = [
            # Assets
            ('1000', 'Cash and Cash Equivalents', 'ASSET', 'debit', None),
            ('1100', 'Bank Account - USD', 'ASSET', 'debit', '1000'),
            ('1200', 'Investments', 'ASSET', 'debit', None),
            ('1300', 'Accounts Receivable', 'ASSET', 'debit', None),
            ('1400', 'Other Assets', 'ASSET', 'debit', None),
            
            # Liabilities
            ('2000', 'Liabilities', 'LIABILITY', 'credit', None),
            ('2100', 'Accounts Payable', 'LIABILITY', 'credit', '2000'),
            ('2200', 'Loans Payable', 'LIABILITY', 'credit', '2000'),
            
            # Equity
            ('3000', 'Equity', 'EQUITY', 'credit', None),
            ('3100', 'Share Capital', 'EQUITY', 'credit', '3000'),
            ('3200', 'Retained Earnings', 'EQUITY', 'credit', '3000'),
            
            # Revenue
            ('4000', 'Revenue', 'REVENUE', 'credit', None),
            ('4100', 'Service Revenue', 'REVENUE', 'credit', '4000'),
            ('4200', 'Investment Income', 'REVENUE', 'credit', '4000'),
            ('4300', 'Other Income', 'REVENUE', 'credit', '4000'),
            
            # Expenses
            ('5000', 'Operating Expenses', 'EXPENSE', 'debit', None),
            ('5100', 'Management Fees', 'EXPENSE', 'debit', '5000'),
            ('5200', 'Professional Fees', 'EXPENSE', 'debit', '5000'),
            ('5300', 'Bank Charges', 'EXPENSE', 'debit', '5000'),
            ('5400', 'Registered Office Fees', 'EXPENSE', 'debit', '5000'),
            ('5500', 'Government Fees', 'EXPENSE', 'debit', '5000'),
        ]
        
        for code, name, acc_type, balance, parent_code in accounts:
            parent = None
            if parent_code:
                parent = ChartOfAccounts.objects.filter(
                    company=company,
                    account_code=parent_code
                ).first()
            
            level = 1 if not parent else parent.level + 1
            is_group = parent is None
            
            ChartOfAccounts.objects.get_or_create(
                company=company,
                account_code=code,
                defaults={
                    'account_name': name,
                    'account_type': acc_type,
                    'normal_balance': balance,
                    'parent_account': parent,
                    'level': level,
                    'is_group_account': is_group,
                    'currency': company.currency,
                }
            )
