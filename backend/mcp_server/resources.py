"""
MCP Resources
Structured data access for LLMs
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


class MCPResource:
    """Base class for MCP resources"""
    
    def __init__(self, company_id: str):
        self.company_id = company_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary for LLM consumption"""
        raise NotImplementedError


class CompanyResource(MCPResource):
    """Company information resource"""
    
    def __init__(self, company_id: str):
        super().__init__(company_id)
        self._load_company()
    
    def _load_company(self):
        """Load company from database"""
        from companies.models import Company
        self.company = Company.objects.get(id=self.company_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Format company data for LLM"""
        return {
            "id": str(self.company.id),
            "name": self.company.name,
            "tax_id": self.company.tax_id,
            "jurisdiction": self.company.jurisdiction,
            "industry": getattr(self.company, 'industry', 'N/A'),
            "fiscal_year_start": str(self.company.fiscal_year_start) if hasattr(self.company, 'fiscal_year_start') else None,
            "chart_of_accounts": self._get_coa_summary(),
            "created_at": self.company.created_at.isoformat(),
        }
    
    def _get_coa_summary(self) -> Dict[str, Any]:
        """Get chart of accounts summary"""
        from companies.models import ChartOfAccounts
        
        accounts = ChartOfAccounts.objects.filter(
            company_id=self.company_id,
            is_active=True
        )
        
        total_count = accounts.count()
        
        # Group by account type
        type_counts = {}
        for account in accounts:
            account_type = account.account_type
            type_counts[account_type] = type_counts.get(account_type, 0) + 1
        
        return {
            "total_accounts": total_count,
            "active_accounts": total_count,
            "account_types": type_counts,
        }


class ChartOfAccountsResource(MCPResource):
    """Chart of Accounts resource with hierarchy"""
    
    def __init__(self, company_id: str):
        super().__init__(company_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Format chart of accounts for LLM"""
        from companies.models import ChartOfAccounts
        
        accounts = ChartOfAccounts.objects.filter(
            company_id=self.company_id,
            is_active=True
        ).order_by('code')
        
        # Build hierarchical structure
        hierarchy = self._build_hierarchy(accounts)
        
        # Get usage statistics
        usage_stats = self._get_usage_stats()
        
        return {
            "company_id": self.company_id,
            "total_accounts": accounts.count(),
            "hierarchy": hierarchy,
            "most_used_accounts": usage_stats,
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    def _build_hierarchy(self, accounts) -> Dict[str, Any]:
        """Build account hierarchy"""
        hierarchy = {
            "ASSET": [],
            "LIABILITY": [],
            "EQUITY": [],
            "REVENUE": [],
            "EXPENSE": [],
        }
        
        for account in accounts:
            account_data = {
                "id": str(account.id),
                "code": account.code,
                "name": account.name,
                "type": account.account_type,
                "is_group": account.is_group_account,
                "parent_code": account.parent_account.code if account.parent_account else None,
            }
            
            account_type = account.account_type
            if account_type in hierarchy:
                hierarchy[account_type].append(account_data)
        
        return hierarchy
    
    def _get_usage_stats(self, days: int = 90) -> List[Dict[str, Any]]:
        """Get most used accounts in last N days"""
        from transactions.models import JournalEntryLine
        from django.db.models import Count
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stats = (
            JournalEntryLine.objects
            .filter(
                journal_entry__company_id=self.company_id,
                journal_entry__date__gte=cutoff_date
            )
            .values('account__code', 'account__name')
            .annotate(usage_count=Count('id'))
            .order_by('-usage_count')[:20]
        )
        
        return [
            {
                "code": stat['account__code'],
                "name": stat['account__name'],
                "usage_count": stat['usage_count']
            }
            for stat in stats
        ]


class TransactionsResource(MCPResource):
    """Transactions resource with filtering"""
    
    def __init__(
        self,
        company_id: str,
        days: int = 30,
        account_code: Optional[str] = None,
        limit: int = 100
    ):
        super().__init__(company_id)
        self.days = days
        self.account_code = account_code
        self.limit = limit
    
    def to_dict(self) -> Dict[str, Any]:
        """Format transactions for LLM"""
        from transactions.models import JournalEntry, JournalEntryLine
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.days)
        
        entries = JournalEntry.objects.filter(
            company_id=self.company_id,
            date__gte=cutoff_date
        ).order_by('-date')[:self.limit]
        
        transactions = []
        for entry in entries:
            lines = entry.lines.select_related('account').all()
            
            # Filter by account if specified
            if self.account_code:
                lines = [line for line in lines if line.account.code == self.account_code]
                if not lines:
                    continue
            
            transaction_data = {
                "id": str(entry.id),
                "date": entry.date.isoformat(),
                "description": entry.description,
                "lines": [
                    {
                        "account_code": line.account.code,
                        "account_name": line.account.name,
                        "debit": float(line.debit) if line.debit else 0,
                        "credit": float(line.credit) if line.credit else 0,
                    }
                    for line in lines
                ],
                "total_debit": float(sum(line.debit for line in lines)),
                "total_credit": float(sum(line.credit for line in lines)),
            }
            
            transactions.append(transaction_data)
        
        return {
            "company_id": self.company_id,
            "period_days": self.days,
            "account_filter": self.account_code,
            "transaction_count": len(transactions),
            "transactions": transactions,
        }


class ReportsResource(MCPResource):
    """Financial reports resource"""
    
    def __init__(
        self,
        company_id: str,
        report_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        super().__init__(company_id)
        self.report_type = report_type
        self.start_date = start_date
        self.end_date = end_date
    
    def to_dict(self) -> Dict[str, Any]:
        """Format report for LLM"""
        if self.report_type == "trial_balance":
            return self._get_trial_balance()
        elif self.report_type == "balance_sheet":
            return self._get_balance_sheet()
        elif self.report_type == "income_statement":
            return self._get_income_statement()
        elif self.report_type == "cash_flow":
            return self._get_cash_flow()
        else:
            return {"error": f"Unknown report type: {self.report_type}"}
    
    def _get_trial_balance(self) -> Dict[str, Any]:
        """Generate trial balance"""
        from reports.trial_balance import generate_trial_balance
        
        trial_balance = generate_trial_balance(
            self.company_id,
            end_date=self.end_date
        )
        
        return {
            "report_type": "trial_balance",
            "company_id": self.company_id,
            "end_date": self.end_date,
            "data": trial_balance,
        }
    
    def _get_balance_sheet(self) -> Dict[str, Any]:
        """Generate balance sheet"""
        from mcp_server.financial_reports import BalanceSheetService
        
        return BalanceSheetService.generate(
            company_id=self.company_id,
            end_date=self.end_date
        )
    
    def _get_income_statement(self) -> Dict[str, Any]:
        """Generate income statement"""
        from mcp_server.financial_reports import IncomeStatementService
        
        return IncomeStatementService.generate(
            company_id=self.company_id,
            start_date=self.start_date,
            end_date=self.end_date
        )
    
    def _get_cash_flow(self) -> Dict[str, Any]:
        """Generate cash flow statement"""
        from mcp_server.financial_reports import CashFlowService
        
        return CashFlowService.generate(
            company_id=self.company_id,
            start_date=self.start_date,
            end_date=self.end_date
        )


# Resource registry
RESOURCE_REGISTRY = {
    "company": CompanyResource,
    "chart_of_accounts": ChartOfAccountsResource,
    "transactions": TransactionsResource,
    "reports": ReportsResource,
}


def get_resource(resource_type: str, company_id: str, **kwargs) -> MCPResource:
    """Get resource by type"""
    resource_class = RESOURCE_REGISTRY.get(resource_type)
    
    if not resource_class:
        raise ValueError(f"Unknown resource type: {resource_type}")
    
    return resource_class(company_id, **kwargs)
