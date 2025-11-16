"""
Test utilities for creating test data.
"""
from datetime import date
from decimal import Decimal
from companies.models import Company, ChartOfAccounts
from django.contrib.auth.models import User


def create_test_company(name="Test Corp", tax_id="12-3456789", owner=None, **kwargs):
    """
    Create a test company with all required fields.
    
    Args:
        name: Company name
        tax_id: Tax ID
        owner: Owner user (will create one if not provided)
        **kwargs: Additional fields
        
    Returns:
        Company instance
    """
    if owner is None:
        # Create a default test user if none provided
        owner = create_test_user(username=f"owner_{tax_id}", password="testpass123")
    
    defaults = {
        'name': name,
        'tax_id': tax_id,
        'jurisdiction': 'US',
        'entity_type': 'US_LLC',
        'fiscal_year_start': date(date.today().year, 1, 1),
        'owner': owner,
    }
    defaults.update(kwargs)
    return Company.objects.create(**defaults)


def create_test_user(username="testuser", password="testpass123", **kwargs):
    """
    Create a test user.
    
    Args:
        username: Username
        password: Password
        **kwargs: Additional fields
        
    Returns:
        User instance
    """
    return User.objects.create_user(username=username, password=password, **kwargs)


def create_test_account(company, account_code="1000", account_name="Test Account", 
                       account_type="ASSET", **kwargs):
    """
    Create a test chart of accounts entry.
    
    Args:
        company: Company instance
        account_code: Account code
        account_name: Account name
        account_type: Account type
        **kwargs: Additional fields
        
    Returns:
        ChartOfAccounts instance
    """
    defaults = {
        'company': company,
        'account_code': account_code,
        'account_name': account_name,
        'account_type': account_type,
    }
    defaults.update(kwargs)
    return ChartOfAccounts.objects.create(**defaults)
