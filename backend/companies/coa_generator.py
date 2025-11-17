"""
Service for generating default Chart of Accounts for companies.
"""
from typing import Dict, List, Any
from companies.models import Company, ChartOfAccounts
from companies.coa import AccountType


class DefaultCOAGenerator:
    """Generate default Chart of Accounts for a company."""
    
    # Default accounts to create for US companies
    DEFAULT_ACCOUNTS = [
        # ASSETS - Level 1
        {'code': '1000', 'name': 'Assets', 'type': 'ASSET', 'is_group': True},
        
        # Current Assets - Level 2
        {'code': '1100', 'name': 'Current Assets', 'type': 'ASSET', 'is_group': True, 'parent': '1000'},
        {'code': '1110', 'name': 'Cash and Cash Equivalents', 'type': 'ASSET', 'is_group': False, 'parent': '1100'},
        {'code': '1120', 'name': 'Accounts Receivable', 'type': 'ASSET', 'is_group': False, 'parent': '1100'},
        {'code': '1130', 'name': 'Inventory', 'type': 'ASSET', 'is_group': False, 'parent': '1100'},
        {'code': '1140', 'name': 'Prepaid Expenses', 'type': 'ASSET', 'is_group': False, 'parent': '1100'},
        
        # Fixed Assets - Level 2
        {'code': '1200', 'name': 'Fixed Assets', 'type': 'ASSET', 'is_group': True, 'parent': '1000'},
        {'code': '1210', 'name': 'Property, Plant & Equipment', 'type': 'ASSET', 'is_group': False, 'parent': '1200'},
        {'code': '1220', 'name': 'Accumulated Depreciation', 'type': 'ASSET', 'is_group': False, 'parent': '1200'},
        
        # LIABILITIES - Level 1
        {'code': '2000', 'name': 'Liabilities', 'type': 'LIABILITY', 'is_group': True},
        
        # Current Liabilities - Level 2
        {'code': '2100', 'name': 'Current Liabilities', 'type': 'LIABILITY', 'is_group': True, 'parent': '2000'},
        {'code': '2110', 'name': 'Accounts Payable', 'type': 'LIABILITY', 'is_group': False, 'parent': '2100'},
        {'code': '2120', 'name': 'Credit Cards Payable', 'type': 'LIABILITY', 'is_group': False, 'parent': '2100'},
        {'code': '2130', 'name': 'Accrued Expenses', 'type': 'LIABILITY', 'is_group': False, 'parent': '2100'},
        {'code': '2140', 'name': 'Payroll Liabilities', 'type': 'LIABILITY', 'is_group': False, 'parent': '2100'},
        
        # Long-term Liabilities - Level 2
        {'code': '2200', 'name': 'Long-term Liabilities', 'type': 'LIABILITY', 'is_group': True, 'parent': '2000'},
        {'code': '2210', 'name': 'Long-term Debt', 'type': 'LIABILITY', 'is_group': False, 'parent': '2200'},
        
        # EQUITY - Level 1
        {'code': '3000', 'name': 'Equity', 'type': 'EQUITY', 'is_group': True},
        {'code': '3100', 'name': 'Owner\'s Equity', 'type': 'EQUITY', 'is_group': False, 'parent': '3000'},
        {'code': '3200', 'name': 'Retained Earnings', 'type': 'EQUITY', 'is_group': False, 'parent': '3000'},
        {'code': '3300', 'name': 'Current Year Earnings', 'type': 'EQUITY', 'is_group': False, 'parent': '3000'},
        
        # REVENUE - Level 1
        {'code': '4000', 'name': 'Revenue', 'type': 'REVENUE', 'is_group': True},
        {'code': '4100', 'name': 'Operating Revenue', 'type': 'REVENUE', 'is_group': True, 'parent': '4000'},
        {'code': '4110', 'name': 'Sales Revenue', 'type': 'REVENUE', 'is_group': False, 'parent': '4100'},
        {'code': '4120', 'name': 'Service Revenue', 'type': 'REVENUE', 'is_group': False, 'parent': '4100'},
        {'code': '4130', 'name': 'Consulting Revenue', 'type': 'REVENUE', 'is_group': False, 'parent': '4100'},
        
        # Other Revenue - Level 2
        {'code': '4900', 'name': 'Other Revenue', 'type': 'REVENUE', 'is_group': True, 'parent': '4000'},
        {'code': '4910', 'name': 'Interest Income', 'type': 'REVENUE', 'is_group': False, 'parent': '4900'},
        {'code': '4920', 'name': 'Miscellaneous Income', 'type': 'REVENUE', 'is_group': False, 'parent': '4900'},
        
        # EXPENSES - Level 1
        {'code': '5000', 'name': 'Expenses', 'type': 'EXPENSE', 'is_group': True},
        
        # Cost of Goods Sold - Level 2
        {'code': '5100', 'name': 'Cost of Goods Sold', 'type': 'EXPENSE', 'is_group': True, 'parent': '5000'},
        {'code': '5110', 'name': 'Materials', 'type': 'EXPENSE', 'is_group': False, 'parent': '5100'},
        {'code': '5120', 'name': 'Labor', 'type': 'EXPENSE', 'is_group': False, 'parent': '5100'},
        {'code': '5130', 'name': 'Manufacturing Overhead', 'type': 'EXPENSE', 'is_group': False, 'parent': '5100'},
        
        # Operating Expenses - Level 2
        {'code': '5200', 'name': 'Operating Expenses', 'type': 'EXPENSE', 'is_group': True, 'parent': '5000'},
        
        # Salaries & Wages - Level 3
        {'code': '5210', 'name': 'Salaries and Wages', 'type': 'EXPENSE', 'is_group': False, 'parent': '5200'},
        {'code': '5220', 'name': 'Payroll Taxes', 'type': 'EXPENSE', 'is_group': False, 'parent': '5200'},
        {'code': '5230', 'name': 'Employee Benefits', 'type': 'EXPENSE', 'is_group': False, 'parent': '5200'},
        
        # Rent & Utilities - Level 3
        {'code': '5240', 'name': 'Rent Expense', 'type': 'EXPENSE', 'is_group': False, 'parent': '5200'},
        {'code': '5250', 'name': 'Utilities', 'type': 'EXPENSE', 'is_group': False, 'parent': '5200'},
        
        # Insurance - Level 3
        {'code': '5260', 'name': 'Insurance', 'type': 'EXPENSE', 'is_group': False, 'parent': '5200'},
        
        # Professional Services - Level 3
        {'code': '5280', 'name': 'Professional Fees', 'type': 'EXPENSE', 'is_group': False, 'parent': '5200'},
        {'code': '5290', 'name': 'Marketing and Advertising', 'type': 'EXPENSE', 'is_group': False, 'parent': '5200'},
        
        # Office Expenses - Level 2
        {'code': '5300', 'name': 'Office Expenses', 'type': 'EXPENSE', 'is_group': True, 'parent': '5000'},
        {'code': '5310', 'name': 'Office Supplies', 'type': 'EXPENSE', 'is_group': False, 'parent': '5300'},
        {'code': '5320', 'name': 'Travel and Entertainment', 'type': 'EXPENSE', 'is_group': False, 'parent': '5300'},
        {'code': '5330', 'name': 'Technology and Software', 'type': 'EXPENSE', 'is_group': False, 'parent': '5300'},
        
        # Financial Expenses - Level 2
        {'code': '5400', 'name': 'Financial Expenses', 'type': 'EXPENSE', 'is_group': True, 'parent': '5000'},
        {'code': '5410', 'name': 'Interest Expense', 'type': 'EXPENSE', 'is_group': False, 'parent': '5400'},
        {'code': '5420', 'name': 'Bank Fees', 'type': 'EXPENSE', 'is_group': False, 'parent': '5400'},
        
        # Taxes - Level 2
        {'code': '5500', 'name': 'Taxes', 'type': 'EXPENSE', 'is_group': True, 'parent': '5000'},
        {'code': '5510', 'name': 'Federal Income Tax', 'type': 'EXPENSE', 'is_group': False, 'parent': '5500'},
        {'code': '5520', 'name': 'State Income Tax', 'type': 'EXPENSE', 'is_group': False, 'parent': '5500'},
        {'code': '5530', 'name': 'Property Tax', 'type': 'EXPENSE', 'is_group': False, 'parent': '5500'},
        
        # Depreciation - Level 2
        {'code': '5700', 'name': 'Depreciation and Amortization', 'type': 'EXPENSE', 'is_group': True, 'parent': '5000'},
        {'code': '5710', 'name': 'Depreciation Expense', 'type': 'EXPENSE', 'is_group': False, 'parent': '5700'},
        
        # Other Expenses - Level 2
        {'code': '5900', 'name': 'Other Expenses', 'type': 'EXPENSE', 'is_group': True, 'parent': '5000'},
        {'code': '5910', 'name': 'Miscellaneous Expense', 'type': 'EXPENSE', 'is_group': False, 'parent': '5900'},
    ]
    
    @classmethod
    def generate(cls, company: Company, overwrite: bool = False) -> Dict[str, Any]:
        """
        Generate default Chart of Accounts for a company.
        
        Args:
            company: Company instance
            overwrite: If True, delete existing accounts and create new ones
            
        Returns:
            dict: Summary of creation
        """
        # Check if company already has accounts
        existing_count = ChartOfAccounts.objects.filter(company=company).count()
        
        if existing_count > 0 and not overwrite:
            return {
                'status': 'skipped',
                'message': f'Company already has {existing_count} accounts. Use overwrite=True to replace.',
                'accounts_created': 0
            }
        
        # Delete existing accounts if overwrite
        if overwrite and existing_count > 0:
            ChartOfAccounts.objects.filter(company=company).delete()
        
        # Create accounts
        created_accounts = {}
        accounts_created = 0
        
        # First pass: create accounts without parent references
        for account_data in cls.DEFAULT_ACCOUNTS:
            account = ChartOfAccounts.objects.create(
                company=company,
                account_code=account_data['code'],
                account_name=account_data['name'],
                account_type=account_data['type'],
                is_group_account=account_data.get('is_group', False),
                is_active=True,
                description=f"Default {account_data['name']} account"
            )
            created_accounts[account_data['code']] = account
            accounts_created += 1
        
        # Second pass: set parent relationships
        for account_data in cls.DEFAULT_ACCOUNTS:
            if 'parent' in account_data:
                parent_code = account_data['parent']
                if parent_code in created_accounts:
                    account = created_accounts[account_data['code']]
                    account.parent_account = created_accounts[parent_code]
                    account.save()
        
        return {
            'status': 'success',
            'message': f'Successfully created {accounts_created} default accounts',
            'accounts_created': accounts_created,
            'company_id': str(company.id),
            'company_name': company.name
        }
    
    @classmethod
    def get_default_accounts_preview(cls) -> List[Dict[str, Any]]:
        """
        Get a preview of default accounts that would be created.
        
        Returns:
            list: List of account dictionaries
        """
        return cls.DEFAULT_ACCOUNTS
