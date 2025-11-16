"""
Chart of Accounts (COA) - Hierarchical Account System

Inspired by Cotizador's COA with 5-level hierarchy adapted for US companies.

Account code format: X.X.X.XX.X (5 levels)
1. Group (1 digit): Asset, Liability, Equity, Revenue, Expense
2. Subgroup (1 digit): Major category
3. Breakdown (1 digit): Subcategory
4. Title (2 digits): Specific account type
5. Subtitle (1 digit): Individual account

Example: 1.1.2.10.1 = Assets > Current Assets > Cash > Bank Account > Main Checking
"""

from enum import Enum


class AccountType(Enum):
    """Account types for US companies."""
    
    # 1. ASSETS
    ASSET = "1"
    CURRENT_ASSET = "1.1"
    CASH = "1.1.1"
    BANK_CHECKING = "1.1.1.10"
    BANK_SAVINGS = "1.1.1.20"
    PETTY_CASH = "1.1.1.30"
    
    ACCOUNTS_RECEIVABLE = "1.1.2"
    AR_TRADE = "1.1.2.10"
    AR_OTHER = "1.1.2.90"
    
    INVENTORY = "1.1.3"
    INVENTORY_RAW_MATERIALS = "1.1.3.10"
    INVENTORY_WORK_IN_PROGRESS = "1.1.3.20"
    INVENTORY_FINISHED_GOODS = "1.1.3.30"
    
    PREPAID_EXPENSES = "1.1.4"
    PREPAID_INSURANCE = "1.1.4.10"
    PREPAID_RENT = "1.1.4.20"
    PREPAID_OTHER = "1.1.4.90"
    
    FIXED_ASSETS = "1.2"
    PROPERTY_PLANT_EQUIPMENT = "1.2.1"
    LAND = "1.2.1.10"
    BUILDINGS = "1.2.1.20"
    MACHINERY = "1.2.1.30"
    VEHICLES = "1.2.1.40"
    FURNITURE_FIXTURES = "1.2.1.50"
    COMPUTERS_EQUIPMENT = "1.2.1.60"
    
    ACCUMULATED_DEPRECIATION = "1.2.2"
    ACCUM_DEPR_BUILDINGS = "1.2.2.20"
    ACCUM_DEPR_MACHINERY = "1.2.2.30"
    ACCUM_DEPR_VEHICLES = "1.2.2.40"
    ACCUM_DEPR_FURNITURE = "1.2.2.50"
    ACCUM_DEPR_COMPUTERS = "1.2.2.60"
    
    INTANGIBLE_ASSETS = "1.3"
    GOODWILL = "1.3.1.10"
    PATENTS = "1.3.1.20"
    TRADEMARKS = "1.3.1.30"
    SOFTWARE = "1.3.1.40"
    
    OTHER_ASSETS = "1.9"
    DEPOSITS = "1.9.1.10"
    INVESTMENTS = "1.9.1.20"
    
    # 2. LIABILITIES
    LIABILITY = "2"
    CURRENT_LIABILITY = "2.1"
    ACCOUNTS_PAYABLE = "2.1.1"
    AP_TRADE = "2.1.1.10"
    AP_OTHER = "2.1.1.90"
    
    ACCRUED_EXPENSES = "2.1.2"
    ACCRUED_SALARIES = "2.1.2.10"
    ACCRUED_TAXES = "2.1.2.20"
    ACCRUED_INTEREST = "2.1.2.30"
    ACCRUED_OTHER = "2.1.2.90"
    
    SHORT_TERM_DEBT = "2.1.3"
    CREDIT_CARDS = "2.1.3.10"
    SHORT_TERM_LOANS = "2.1.3.20"
    CURRENT_PORTION_LONG_TERM_DEBT = "2.1.3.30"
    
    PAYROLL_LIABILITIES = "2.1.4"
    FEDERAL_INCOME_TAX_PAYABLE = "2.1.4.10"
    STATE_INCOME_TAX_PAYABLE = "2.1.4.20"
    FICA_PAYABLE = "2.1.4.30"
    MEDICARE_PAYABLE = "2.1.4.40"
    
    LONG_TERM_LIABILITY = "2.2"
    LONG_TERM_DEBT = "2.2.1"
    BANK_LOANS = "2.2.1.10"
    MORTGAGES = "2.2.1.20"
    BONDS_PAYABLE = "2.2.1.30"
    
    # 3. EQUITY
    EQUITY = "3"
    OWNERS_EQUITY = "3.1"
    COMMON_STOCK = "3.1.1.10"
    PREFERRED_STOCK = "3.1.1.20"
    ADDITIONAL_PAID_IN_CAPITAL = "3.1.1.30"
    TREASURY_STOCK = "3.1.1.40"
    
    RETAINED_EARNINGS = "3.2"
    RETAINED_EARNINGS_CURRENT = "3.2.1.10"
    RETAINED_EARNINGS_PRIOR = "3.2.1.20"
    
    DIVIDENDS = "3.3"
    DIVIDENDS_PAID = "3.3.1.10"
    
    # 4. REVENUE
    REVENUE = "4"
    OPERATING_REVENUE = "4.1"
    SALES_REVENUE = "4.1.1"
    PRODUCT_SALES = "4.1.1.10"
    SERVICE_REVENUE = "4.1.1.20"
    CONSULTING_REVENUE = "4.1.1.30"
    
    SALES_RETURNS_ALLOWANCES = "4.1.2"
    SALES_RETURNS = "4.1.2.10"
    SALES_DISCOUNTS = "4.1.2.20"
    
    OTHER_REVENUE = "4.9"
    INTEREST_INCOME = "4.9.1.10"
    DIVIDEND_INCOME = "4.9.1.20"
    RENTAL_INCOME = "4.9.1.30"
    GAIN_ON_SALE_ASSETS = "4.9.1.40"
    MISCELLANEOUS_INCOME = "4.9.1.90"
    
    # 5. EXPENSES
    EXPENSE = "5"
    COST_OF_GOODS_SOLD = "5.1"
    COGS_MATERIALS = "5.1.1.10"
    COGS_LABOR = "5.1.1.20"
    COGS_OVERHEAD = "5.1.1.30"
    
    OPERATING_EXPENSES = "5.2"
    SALARIES_WAGES = "5.2.1"
    SALARIES_OFFICERS = "5.2.1.10"
    SALARIES_EMPLOYEES = "5.2.1.20"
    WAGES_HOURLY = "5.2.1.30"
    
    PAYROLL_TAXES = "5.2.2"
    FICA_EXPENSE = "5.2.2.10"
    MEDICARE_EXPENSE = "5.2.2.20"
    FUTA_EXPENSE = "5.2.2.30"
    SUTA_EXPENSE = "5.2.2.40"
    
    EMPLOYEE_BENEFITS = "5.2.3"
    HEALTH_INSURANCE = "5.2.3.10"
    RETIREMENT_401K = "5.2.3.20"
    WORKERS_COMPENSATION = "5.2.3.30"
    
    RENT_EXPENSE = "5.2.4"
    RENT_OFFICE = "5.2.4.10"
    RENT_WAREHOUSE = "5.2.4.20"
    
    UTILITIES = "5.2.5"
    ELECTRICITY = "5.2.5.10"
    WATER = "5.2.5.20"
    GAS = "5.2.5.30"
    INTERNET_PHONE = "5.2.5.40"
    
    INSURANCE = "5.2.6"
    GENERAL_LIABILITY = "5.2.6.10"
    PROPERTY_INSURANCE = "5.2.6.20"
    PROFESSIONAL_LIABILITY = "5.2.6.30"
    
    DEPRECIATION = "5.2.7"
    DEPRECIATION_EXPENSE = "5.2.7.10"
    AMORTIZATION_EXPENSE = "5.2.7.20"
    
    PROFESSIONAL_FEES = "5.2.8"
    ACCOUNTING_FEES = "5.2.8.10"
    LEGAL_FEES = "5.2.8.20"
    CONSULTING_FEES = "5.2.8.30"
    
    MARKETING_ADVERTISING = "5.2.9"
    ADVERTISING = "5.2.9.10"
    MARKETING_CAMPAIGNS = "5.2.9.20"
    WEBSITE = "5.2.9.30"
    
    OFFICE_EXPENSES = "5.3"
    OFFICE_SUPPLIES = "5.3.1.10"
    POSTAGE_SHIPPING = "5.3.1.20"
    PRINTING = "5.3.1.30"
    
    TRAVEL_ENTERTAINMENT = "5.3.2"
    TRAVEL = "5.3.2.10"
    MEALS_ENTERTAINMENT = "5.3.2.20"
    
    VEHICLE_EXPENSES = "5.3.3"
    FUEL = "5.3.3.10"
    MAINTENANCE_REPAIRS = "5.3.3.20"
    VEHICLE_INSURANCE = "5.3.3.30"
    
    TECHNOLOGY = "5.3.4"
    SOFTWARE_SUBSCRIPTIONS = "5.3.4.10"
    HARDWARE = "5.3.4.20"
    IT_SUPPORT = "5.3.4.30"
    
    FINANCIAL_EXPENSES = "5.4"
    INTEREST_EXPENSE = "5.4.1.10"
    BANK_FEES = "5.4.1.20"
    CREDIT_CARD_FEES = "5.4.1.30"
    
    TAXES = "5.5"
    FEDERAL_INCOME_TAX = "5.5.1.10"
    STATE_INCOME_TAX = "5.5.1.20"
    PROPERTY_TAX = "5.5.1.30"
    SALES_TAX = "5.5.1.40"
    
    OTHER_EXPENSES = "5.9"
    MISCELLANEOUS_EXPENSE = "5.9.1.10"
    LOSS_ON_SALE_ASSETS = "5.9.1.20"
    BAD_DEBT_EXPENSE = "5.9.1.30"


class COAHelper:
    """Helper class for Chart of Accounts operations."""
    
    @staticmethod
    def get_level(account_code):
        """
        Get the level of an account code.
        
        Args:
            account_code: Account code string (e.g., "1.1.2.10")
            
        Returns:
            int: Level (1-5)
        """
        return len([p for p in account_code.split('.') if p and p != '0'])
    
    @staticmethod
    def get_parent(account_code):
        """
        Get the parent account code.
        
        Args:
            account_code: Account code string
            
        Returns:
            str: Parent account code or None if top-level
        """
        parts = account_code.split('.')
        if len(parts) <= 1:
            return None
        return '.'.join(parts[:-1])
    
    @staticmethod
    def get_children(account_code, all_accounts):
        """
        Get all direct children of an account.
        
        Args:
            account_code: Parent account code
            all_accounts: List of all account codes
            
        Returns:
            list: List of child account codes
        """
        children = []
        for acc in all_accounts:
            if acc.startswith(account_code + '.'):
                # Check if it's a direct child
                remaining = acc[len(account_code)+1:]
                if '.' not in remaining:
                    children.append(acc)
        return children
    
    @staticmethod
    def is_group_account(account_code):
        """
        Check if an account is a group (non-transactional) account.
        
        Args:
            account_code: Account code string
            
        Returns:
            bool: True if group account
        """
        level = COAHelper.get_level(account_code)
        return level < 5  # Only level 5 accounts are transactional
    
    @staticmethod
    def get_account_type_name(account_code):
        """
        Get the human-readable name for an account type.
        
        Args:
            account_code: Account code string
            
        Returns:
            str: Account type name
        """
        first_digit = account_code[0]
        type_names = {
            '1': 'Asset',
            '2': 'Liability',
            '3': 'Equity',
            '4': 'Revenue',
            '5': 'Expense',
        }
        return type_names.get(first_digit, 'Unknown')
    
    @staticmethod
    def get_normal_balance(account_code):
        """
        Get the normal balance (debit or credit) for an account.
        
        Args:
            account_code: Account code string
            
        Returns:
            str: 'debit' or 'credit'
        """
        first_digit = account_code[0]
        # Assets and Expenses have debit normal balance
        # Liabilities, Equity, and Revenue have credit normal balance
        if first_digit in ['1', '5']:
            return 'debit'
        else:
            return 'credit'

