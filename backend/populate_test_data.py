import os
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from companies.models import Company, ChartOfAccounts
from transactions.models import Transaction, JournalEntry, JournalEntryLine
from documents.models import Document

print("🚀 Populating database with test data...")

# Get or create test user
user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    user.set_password('admin123')
    user.save()
print(f"✅ User: {user.username}")

# Create test company
from datetime import date
company, created = Company.objects.get_or_create(
    name='Acme Corporation',
    defaults={
        'tax_id': '12-3456789',
        'address': '123 Main St',
        'city': 'New York',
        'state': 'NY',
        'zip_code': '10001',
        'phone': '(555) 123-4567',
        'email': 'info@acmecorp.com',
        'fiscal_year_start': date(2024, 1, 1),
        'owner': user
    }
)
print(f"✅ Company: {company.name}")

# Create Chart of Accounts
accounts_data = [
    ('1000', 'Cash', 'ASSET', 'Cash and cash equivalents'),
    ('1100', 'Accounts Receivable', 'ASSET', 'Money owed by customers'),
    ('1200', 'Inventory', 'ASSET', 'Products for sale'),
    ('1500', 'Equipment', 'ASSET', 'Office equipment and furniture'),
    ('2000', 'Accounts Payable', 'LIABILITY', 'Money owed to suppliers'),
    ('2100', 'Credit Card', 'LIABILITY', 'Credit card balances'),
    ('2500', 'Loans Payable', 'LIABILITY', 'Bank loans'),
    ('3000', 'Owner Equity', 'EQUITY', 'Owner investment'),
    ('3100', 'Retained Earnings', 'EQUITY', 'Accumulated profits'),
    ('4000', 'Sales Revenue', 'REVENUE', 'Revenue from sales'),
    ('4100', 'Service Revenue', 'REVENUE', 'Revenue from services'),
    ('5000', 'Cost of Goods Sold', 'EXPENSE', 'Direct costs of products sold'),
    ('6000', 'Rent Expense', 'EXPENSE', 'Office rent'),
    ('6100', 'Salaries Expense', 'EXPENSE', 'Employee salaries'),
    ('6200', 'Utilities Expense', 'EXPENSE', 'Electricity, water, internet'),
    ('6300', 'Office Supplies', 'EXPENSE', 'Office supplies and materials'),
]

accounts = {}
for code, name, acc_type, desc in accounts_data:
    account, created = ChartOfAccounts.objects.get_or_create(
        company=company,
        account_code=code,
        defaults={
            'account_name': name,
            'account_type': acc_type,
            'description': desc
        }
    )
    accounts[code] = account
    if created:
        print(f"  ✓ Account: {code} - {name}")

# Create sample transactions
transactions_data = [
    # Revenue transactions
    {
        'date': datetime.now() - timedelta(days=30),
        'description': 'Product sales - January',
        'amount': Decimal('15000.00'),
        'category': 'REVENUE',
        'debit_account': '1000',  # Cash
        'credit_account': '4000',  # Sales Revenue
    },
    {
        'date': datetime.now() - timedelta(days=25),
        'description': 'Consulting services',
        'amount': Decimal('8500.00'),
        'category': 'REVENUE',
        'debit_account': '1000',  # Cash
        'credit_account': '4100',  # Service Revenue
    },
    # Expense transactions
    {
        'date': datetime.now() - timedelta(days=20),
        'description': 'Office rent - January',
        'amount': Decimal('3000.00'),
        'category': 'EXPENSE',
        'debit_account': '6000',  # Rent Expense
        'credit_account': '1000',  # Cash
    },
    {
        'date': datetime.now() - timedelta(days=15),
        'description': 'Employee salaries',
        'amount': Decimal('12000.00'),
        'category': 'EXPENSE',
        'debit_account': '6100',  # Salaries Expense
        'credit_account': '1000',  # Cash
    },
    {
        'date': datetime.now() - timedelta(days=10),
        'description': 'Utilities bill',
        'amount': Decimal('450.00'),
        'category': 'EXPENSE',
        'debit_account': '6200',  # Utilities Expense
        'credit_account': '2100',  # Credit Card
    },
    {
        'date': datetime.now() - timedelta(days=5),
        'description': 'Office supplies purchase',
        'amount': Decimal('850.00'),
        'category': 'EXPENSE',
        'debit_account': '6300',  # Office Supplies
        'credit_account': '1000',  # Cash
    },
    # Asset purchase
    {
        'date': datetime.now() - timedelta(days=45),
        'description': 'Computer equipment',
        'amount': Decimal('5000.00'),
        'category': 'ASSET',
        'debit_account': '1500',  # Equipment
        'credit_account': '1000',  # Cash
    },
]

print("\n📝 Creating transactions...")
for trans_data in transactions_data:
    # Create transaction
    transaction, created = Transaction.objects.get_or_create(
        company=company,
        date=trans_data['date'],
        description=trans_data['description'],
        defaults={
            'amount': trans_data['amount'],
            'is_validated': True,
            'validated_by': user,
            'validated_at': trans_data['date']
        }
    )
    
    if created:
        # Create journal entry
        journal_entry = JournalEntry.objects.create(
            company=company,
            date=trans_data['date'],
            description=trans_data['description'],
            reference=f"JE-{str(transaction.id)[:8]}",
            transaction=transaction
        )
        
        # Debit line
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=accounts[trans_data['debit_account']],
            debit=trans_data['amount'],
            credit=Decimal('0.00')
        )
        
        # Credit line
        JournalEntryLine.objects.create(
            journal_entry=journal_entry,
            account=accounts[trans_data['credit_account']],
            debit=Decimal('0.00'),
            credit=trans_data['amount']
        )
        
        print(f"  ✓ {trans_data['description']}: ${trans_data['amount']}")

# Create sample document
doc, created = Document.objects.get_or_create(
    company=company,
    file_name='sample_bank_statement.pdf',
    defaults={
        'file_type': 'PDF',
        'file_path': '/uploads/sample_bank_statement.pdf',
        'file_size': 1024000,
        'status': 'COMPLETED',
        'uploaded_by': user
    }
)
if created:
    print(f"\n📄 Document: {doc.file_name}")

print("\n✅ Database populated successfully!")
print(f"\n📊 Summary:")
print(f"  - Company: {company.name}")
print(f"  - Accounts: {ChartOfAccounts.objects.filter(company=company).count()}")
print(f"  - Transactions: {Transaction.objects.filter(company=company).count()}")
print(f"  - Journal Entries: {JournalEntry.objects.filter(company=company).count()}")
print(f"  - Documents: {Document.objects.filter(company=company).count()}")

