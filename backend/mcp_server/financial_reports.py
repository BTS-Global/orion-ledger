"""
Financial Reports Service for MCP
Generates Balance Sheet, Income Statement, and Cash Flow
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Q

logger = logging.getLogger(__name__)


class BalanceSheetService:
    """Generate Balance Sheet (Balanço Patrimonial)"""
    
    @staticmethod
    def generate(company_id: str, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate balance sheet showing Assets, Liabilities, and Equity
        
        Args:
            company_id: Company UUID
            end_date: Date for the balance sheet (YYYY-MM-DD)
        
        Returns:
            Dictionary with balance sheet data
        """
        from companies.models import Company, ChartOfAccounts
        from transactions.models import JournalEntryLine
        
        try:
            company = Company.objects.get(id=company_id)
            
            if end_date:
                date_filter = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                date_filter = datetime.now().date()
            
            # Get all accounts with balances
            accounts = ChartOfAccounts.objects.filter(
                company=company,
                is_active=True
            ).order_by('code')
            
            # Initialize structure
            assets = {
                "current": [],
                "non_current": [],
                "total": Decimal('0.00')
            }
            liabilities = {
                "current": [],
                "non_current": [],
                "total": Decimal('0.00')
            }
            equity = {
                "items": [],
                "total": Decimal('0.00')
            }
            
            # Process each account
            for account in accounts:
                balance = BalanceSheetService._calculate_account_balance(
                    account, date_filter
                )
                
                if abs(balance) < 0.01:  # Skip zero balances
                    continue
                
                account_data = {
                    "code": account.code,
                    "name": account.name,
                    "balance": float(balance)
                }
                
                # Classify by account type
                if account.account_type == 'ASSET':
                    # Determine if current or non-current
                    # Simple heuristic: codes starting with 1.1 are current
                    if account.code.startswith('1.1') or 'circulante' in account.name.lower():
                        assets["current"].append(account_data)
                    else:
                        assets["non_current"].append(account_data)
                    assets["total"] += balance
                    
                elif account.account_type == 'LIABILITY':
                    if account.code.startswith('2.1') or 'circulante' in account.name.lower():
                        liabilities["current"].append(account_data)
                    else:
                        liabilities["non_current"].append(account_data)
                    liabilities["total"] += balance
                    
                elif account.account_type == 'EQUITY':
                    equity["items"].append(account_data)
                    equity["total"] += balance
            
            # Calculate totals
            total_assets = float(assets["total"])
            total_liabilities = float(liabilities["total"])
            total_equity = float(equity["total"])
            
            # Verify accounting equation: Assets = Liabilities + Equity
            is_balanced = abs(total_assets - (total_liabilities + total_equity)) < 0.01
            
            return {
                "report_type": "balance_sheet",
                "company_id": company_id,
                "company_name": company.name,
                "date": end_date or datetime.now().date().isoformat(),
                "assets": {
                    "current": assets["current"],
                    "current_total": float(sum(a["balance"] for a in assets["current"])),
                    "non_current": assets["non_current"],
                    "non_current_total": float(sum(a["balance"] for a in assets["non_current"])),
                    "total": total_assets
                },
                "liabilities": {
                    "current": liabilities["current"],
                    "current_total": float(sum(l["balance"] for l in liabilities["current"])),
                    "non_current": liabilities["non_current"],
                    "non_current_total": float(sum(l["balance"] for l in liabilities["non_current"])),
                    "total": total_liabilities
                },
                "equity": {
                    "items": equity["items"],
                    "total": total_equity
                },
                "totals": {
                    "total_assets": total_assets,
                    "total_liabilities_and_equity": total_liabilities + total_equity,
                    "is_balanced": is_balanced,
                    "difference": total_assets - (total_liabilities + total_equity)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating balance sheet: {e}")
            return {
                "error": str(e),
                "report_type": "balance_sheet",
                "company_id": company_id
            }
    
    @staticmethod
    def _calculate_account_balance(account, end_date) -> Decimal:
        """Calculate balance for an account up to end_date"""
        from transactions.models import JournalEntryLine
        
        lines = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__date__lte=end_date
        ).aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        total_debit = lines['total_debit'] or Decimal('0.00')
        total_credit = lines['total_credit'] or Decimal('0.00')
        
        # Balance based on normal balance type
        if account.normal_balance == 'debit':
            return total_debit - total_credit
        else:
            return total_credit - total_debit


class IncomeStatementService:
    """Generate Income Statement (DRE - Demonstração do Resultado do Exercício)"""
    
    @staticmethod
    def generate(
        company_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate income statement showing Revenue, Expenses, and Net Income
        
        Args:
            company_id: Company UUID
            start_date: Start date (YYYY-MM-DD), defaults to beginning of current year
            end_date: End date (YYYY-MM-DD), defaults to today
        
        Returns:
            Dictionary with income statement data
        """
        from companies.models import Company, ChartOfAccounts
        from transactions.models import JournalEntryLine
        
        try:
            company = Company.objects.get(id=company_id)
            
            # Default dates
            if not end_date:
                end_date_obj = datetime.now().date()
            else:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if not start_date:
                start_date_obj = datetime(end_date_obj.year, 1, 1).date()
            else:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Get revenue and expense accounts
            accounts = ChartOfAccounts.objects.filter(
                company=company,
                is_active=True,
                account_type__in=['REVENUE', 'EXPENSE']
            ).order_by('code')
            
            # Initialize structure
            revenue = {
                "operating": [],
                "non_operating": [],
                "total": Decimal('0.00')
            }
            expenses = {
                "operating": [],
                "non_operating": [],
                "total": Decimal('0.00')
            }
            
            # Process each account
            for account in accounts:
                balance = IncomeStatementService._calculate_period_balance(
                    account, start_date_obj, end_date_obj
                )
                
                if abs(balance) < 0.01:  # Skip zero balances
                    continue
                
                account_data = {
                    "code": account.code,
                    "name": account.name,
                    "amount": float(abs(balance))  # Always positive in IS
                }
                
                # Classify accounts
                if account.account_type == 'REVENUE':
                    # Determine if operating or non-operating
                    if 'operacion' in account.name.lower() or account.code.startswith('4.1'):
                        revenue["operating"].append(account_data)
                    else:
                        revenue["non_operating"].append(account_data)
                    revenue["total"] += abs(balance)
                    
                elif account.account_type == 'EXPENSE':
                    if 'operacion' in account.name.lower() or account.code.startswith('5.1'):
                        expenses["operating"].append(account_data)
                    else:
                        expenses["non_operating"].append(account_data)
                    expenses["total"] += abs(balance)
            
            # Calculate metrics
            total_revenue = float(revenue["total"])
            total_expenses = float(expenses["total"])
            operating_income = sum(r["amount"] for r in revenue["operating"]) - \
                             sum(e["amount"] for e in expenses["operating"])
            net_income = total_revenue - total_expenses
            
            # Calculate margin
            margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
            
            return {
                "report_type": "income_statement",
                "company_id": company_id,
                "company_name": company.name,
                "period": {
                    "start_date": start_date_obj.isoformat(),
                    "end_date": end_date_obj.isoformat(),
                    "days": (end_date_obj - start_date_obj).days + 1
                },
                "revenue": {
                    "operating": revenue["operating"],
                    "operating_total": sum(r["amount"] for r in revenue["operating"]),
                    "non_operating": revenue["non_operating"],
                    "non_operating_total": sum(r["amount"] for r in revenue["non_operating"]),
                    "total": total_revenue
                },
                "expenses": {
                    "operating": expenses["operating"],
                    "operating_total": sum(e["amount"] for e in expenses["operating"]),
                    "non_operating": expenses["non_operating"],
                    "non_operating_total": sum(e["amount"] for e in expenses["non_operating"]),
                    "total": total_expenses
                },
                "metrics": {
                    "gross_revenue": total_revenue,
                    "total_expenses": total_expenses,
                    "operating_income": operating_income,
                    "net_income": net_income,
                    "net_margin_percent": round(margin, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating income statement: {e}")
            return {
                "error": str(e),
                "report_type": "income_statement",
                "company_id": company_id
            }
    
    @staticmethod
    def _calculate_period_balance(account, start_date, end_date) -> Decimal:
        """Calculate balance for period"""
        from transactions.models import JournalEntryLine
        
        lines = JournalEntryLine.objects.filter(
            account=account,
            journal_entry__date__gte=start_date,
            journal_entry__date__lte=end_date
        ).aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        total_debit = lines['total_debit'] or Decimal('0.00')
        total_credit = lines['total_credit'] or Decimal('0.00')
        
        # For income statement, we want the net change
        if account.account_type == 'REVENUE':
            # Revenue has credit normal balance
            return total_credit - total_debit
        else:  # EXPENSE
            # Expense has debit normal balance
            return total_debit - total_credit


class CashFlowService:
    """Generate Cash Flow Statement"""
    
    @staticmethod
    def generate(
        company_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate cash flow statement
        
        Args:
            company_id: Company UUID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Dictionary with cash flow data
        """
        from companies.models import Company
        from transactions.models import JournalEntryLine, JournalEntry
        
        try:
            company = Company.objects.get(id=company_id)
            
            # Default dates
            if not end_date:
                end_date_obj = datetime.now().date()
            else:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if not start_date:
                start_date_obj = datetime(end_date_obj.year, 1, 1).date()
            else:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # Get all cash/bank accounts (simplified - assumes accounts starting with 1.01)
            cash_accounts = company.chartofaccounts_set.filter(
                is_active=True,
                code__startswith='1.01'  # Cash and banks
            )
            
            # Get all transactions affecting cash in the period
            cash_transactions = JournalEntryLine.objects.filter(
                account__in=cash_accounts,
                journal_entry__date__gte=start_date_obj,
                journal_entry__date__lte=end_date_obj
            ).select_related('account', 'journal_entry').order_by('journal_entry__date')
            
            # Classify transactions (simplified categorization)
            operating = []
            investing = []
            financing = []
            
            for line in cash_transactions:
                # Net cash impact (positive = cash in, negative = cash out)
                cash_impact = float(line.debit - line.credit)
                
                transaction_data = {
                    "date": line.journal_entry.date.isoformat(),
                    "description": line.journal_entry.description,
                    "amount": cash_impact,
                    "account": line.account.name
                }
                
                # Simple classification based on account or description keywords
                desc_lower = line.journal_entry.description.lower()
                
                if any(word in desc_lower for word in ['receita', 'venda', 'cliente', 'fornecedor', 'despesa', 'pagamento']):
                    operating.append(transaction_data)
                elif any(word in desc_lower for word in ['investimento', 'ativo', 'equipamento', 'imóvel']):
                    investing.append(transaction_data)
                elif any(word in desc_lower for word in ['empréstimo', 'financiamento', 'capital', 'dividendo']):
                    financing.append(transaction_data)
                else:
                    operating.append(transaction_data)  # Default to operating
            
            # Calculate totals
            operating_total = sum(t["amount"] for t in operating)
            investing_total = sum(t["amount"] for t in investing)
            financing_total = sum(t["amount"] for t in financing)
            net_change = operating_total + investing_total + financing_total
            
            # Get beginning and ending cash balances
            beginning_balance = CashFlowService._get_cash_balance(
                company_id, start_date_obj - timedelta(days=1)
            )
            ending_balance = beginning_balance + net_change
            
            return {
                "report_type": "cash_flow",
                "company_id": company_id,
                "company_name": company.name,
                "period": {
                    "start_date": start_date_obj.isoformat(),
                    "end_date": end_date_obj.isoformat()
                },
                "operating_activities": {
                    "transactions": operating,
                    "total": operating_total
                },
                "investing_activities": {
                    "transactions": investing,
                    "total": investing_total
                },
                "financing_activities": {
                    "transactions": financing,
                    "total": financing_total
                },
                "summary": {
                    "net_cash_from_operations": operating_total,
                    "net_cash_from_investing": investing_total,
                    "net_cash_from_financing": financing_total,
                    "net_change_in_cash": net_change,
                    "beginning_cash_balance": beginning_balance,
                    "ending_cash_balance": ending_balance
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating cash flow: {e}")
            return {
                "error": str(e),
                "report_type": "cash_flow",
                "company_id": company_id
            }
    
    @staticmethod
    def _get_cash_balance(company_id: str, date) -> float:
        """Get cash balance at a specific date"""
        from companies.models import Company
        from transactions.models import JournalEntryLine
        
        company = Company.objects.get(id=company_id)
        cash_accounts = company.chartofaccounts_set.filter(
            is_active=True,
            code__startswith='1.01'
        )
        
        lines = JournalEntryLine.objects.filter(
            account__in=cash_accounts,
            journal_entry__date__lte=date
        ).aggregate(
            total_debit=Sum('debit'),
            total_credit=Sum('credit')
        )
        
        total_debit = lines['total_debit'] or Decimal('0.00')
        total_credit = lines['total_credit'] or Decimal('0.00')
        
        return float(total_debit - total_credit)
