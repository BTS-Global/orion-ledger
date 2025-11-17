"""
MCP Tools
Executable functions that LLMs can call
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Tool Parameter Models

class ClassifyTransactionParams(BaseModel):
    """Parameters for classify_transaction tool"""
    company_id: str = Field(..., description="Company ID")
    description: str = Field(..., description="Transaction description")
    amount: float = Field(..., description="Transaction amount")
    date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    vendor: Optional[str] = Field(None, description="Vendor/payee name")
    document_number: Optional[str] = Field(
        None, description="Document/invoice number"
    )


class CreateJournalEntryParams(BaseModel):
    """Parameters for create_journal_entry tool"""
    company_id: str = Field(..., description="Company ID")
    date: str = Field(..., description="Entry date (YYYY-MM-DD)")
    description: str = Field(..., description="Entry description")
    lines: List[Dict[str, Any]] = Field(..., description="Journal entry lines")


class AuditTransactionsParams(BaseModel):
    """Parameters for audit_transactions tool"""
    company_id: str = Field(..., description="Company ID")
    start_date: Optional[str] = Field(
        None, description="Start date (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        None, description="End date (YYYY-MM-DD)"
    )
    check_duplicates: bool = Field(
        True, description="Check for duplicate transactions"
    )
    check_unusual_amounts: bool = Field(
        True, description="Check for unusual amounts"
    )
    check_inconsistencies: bool = Field(
        True, description="Check for classification inconsistencies"
    )


class AnalyzeDocumentParams(BaseModel):
    """Parameters for analyze_document tool"""
    company_id: str = Field(..., description="Company ID")
    document_path: str = Field(..., description="Path to document file")
    document_type: Optional[str] = Field(
        None, description="Type hint: invoice, receipt, statement"
    )


class GenerateCustomReportParams(BaseModel):
    """Parameters for generate_custom_report tool"""
    company_id: str = Field(..., description="Company ID")
    query: str = Field(
        ..., description="Natural language query for the report"
    )
    start_date: Optional[str] = Field(
        None, description="Start date (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        None, description="End date (YYYY-MM-DD)"
    )
    limit: Optional[int] = Field(100, description="Maximum number of results")


# Tool Implementations

async def classify_transaction_tool(
    params: ClassifyTransactionParams
) -> Dict[str, Any]:
    """
    Classify a transaction using AI with historical context.
    Returns suggested account with confidence level.
    """
    try:
        # Import here to avoid circular dependency
        from core.rag_service import rag_service
        
        # Generate embedding for the transaction
        transaction_text = (
            f"{params.description} {params.vendor or ''} {params.amount}"
        )
        embedding = rag_service.generate_embedding(transaction_text)
        
        # Find similar transactions
        similar_transactions = rag_service.find_similar_transactions(
            embedding=embedding,
            company_id=params.company_id,
            top_k=10
        )
        
        # Create augmented prompt with context
        prompt = rag_service.augment_prompt_with_context(
            {
                "description": params.description,
                "amount": params.amount,
                "date": params.date,
                "vendor": params.vendor,
                "document_number": params.document_number,
            },
            params.company_id
        )
        
        # Call LLM for classification
        from core.ai_views import classify_with_llm
        
        classification = await classify_with_llm(
            prompt=prompt,
            similar_transactions=similar_transactions,
            company_id=params.company_id
        )
        
        # Record prediction for learning
        from core.feedback_service import record_ai_prediction
        
        await record_ai_prediction(
            company_id=params.company_id,
            transaction_data=params.dict(),
            prediction=classification
        )
        
        return {
            "success": True,
            "suggested_account": classification.get("account"),
            "confidence": classification.get("confidence", 0.0),
            "similar_transactions": similar_transactions[:5],
            "reasoning": classification.get("reasoning", ""),
        }
        
    except Exception as e:
        logger.error(f"Error in classify_transaction_tool: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def create_journal_entry_tool(
    params: CreateJournalEntryParams
) -> Dict[str, Any]:
    """
    Create a journal entry with double-entry validation.
    AI suggests counter-entries if not provided.
    """
    try:
        from transactions.models import JournalEntry, JournalEntryLine
        from companies.models import ChartOfAccounts
        from decimal import Decimal
        
        # Validate date
        entry_date = datetime.strptime(params.date, "%Y-%m-%d").date()
        
        # Validate lines
        total_debit = Decimal("0")
        total_credit = Decimal("0")
        
        validated_lines = []
        
        for line in params.lines:
            account_code = line.get("account_code")
            debit = Decimal(str(line.get("debit", 0)))
            credit = Decimal(str(line.get("credit", 0)))
            
            # Validate account exists
            try:
                account = ChartOfAccounts.objects.get(
                    company_id=params.company_id,
                    code=account_code,
                    is_active=True
                )
            except ChartOfAccounts.DoesNotExist:
                return {
                    "success": False,
                    "error": f"Account {account_code} not found",
                }
            
            total_debit += debit
            total_credit += credit
            
            validated_lines.append({
                "account": account,
                "debit": debit,
                "credit": credit,
                "description": line.get("description", ""),
            })
        
        # Validate double-entry
        if total_debit != total_credit:
            return {
                "success": False,
                "error": (
                    f"Debits ({total_debit}) do not equal "
                    f"credits ({total_credit})"
                ),
            }
        
        # Create journal entry
        entry = JournalEntry.objects.create(
            company_id=params.company_id,
            date=entry_date,
            description=params.description,
            created_by_ai=True,
        )
        
        # Create lines
        for line_data in validated_lines:
            JournalEntryLine.objects.create(
                journal_entry=entry,
                account=line_data["account"],
                debit=line_data["debit"],
                credit=line_data["credit"],
                description=line_data["description"],
            )
        
        return {
            "success": True,
            "journal_entry_id": str(entry.id),
            "date": str(entry.date),
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "lines_count": len(validated_lines),
        }
        
    except Exception as e:
        logger.error(f"Error in create_journal_entry_tool: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def audit_transactions_tool(
    params: AuditTransactionsParams
) -> Dict[str, Any]:
    """
    Analyze transactions for anomalies and inconsistencies.
    AI learns normal patterns and identifies deviations.
    """
    try:
        from transactions.models import JournalEntry
        
        # Build query
        query = JournalEntry.objects.filter(company_id=params.company_id)
        
        if params.start_date:
            query = query.filter(date__gte=params.start_date)
        if params.end_date:
            query = query.filter(date__lte=params.end_date)
        
        entries = query.select_related().prefetch_related('lines__account')
        
        anomalies = []
        
        # Check for duplicates
        if params.check_duplicates:
            duplicates = _find_duplicates(entries)
            anomalies.extend(duplicates)
        
        # Check for unusual amounts
        if params.check_unusual_amounts:
            unusual = _find_unusual_amounts(entries, params.company_id)
            anomalies.extend(unusual)
        
        # Check for inconsistencies
        if params.check_inconsistencies:
            inconsistencies = _find_inconsistencies(entries, params.company_id)
            anomalies.extend(inconsistencies)
        
        # Count by severity
        critical_count = sum(
            1 for a in anomalies if a["severity"] == "critical"
        )
        warning_count = sum(
            1 for a in anomalies if a["severity"] == "warning"
        )
        
        return {
            "success": True,
            "transactions_analyzed": entries.count(),
            "anomalies_found": len(anomalies),
            "critical": critical_count,
            "warnings": warning_count,
            "items": anomalies,
        }
        
    except Exception as e:
        logger.error(f"Error in audit_transactions_tool: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def analyze_document_tool(
    params: AnalyzeDocumentParams
) -> Dict[str, Any]:
    """
    Analyze a document (PDF, image) and extract accounting information.
    Returns structured transaction data ready for import.
    """
    try:
        # Import document processing service
        from documents.tasks import process_document_with_llm
        from documents.models import Document
        
        # Get or create document record
        document = Document.objects.filter(
            company_id=params.company_id,
            file_path=params.document_path
        ).first()
        
        if not document:
            # Create new document record
            document = Document.objects.create(
                company_id=params.company_id,
                file_path=params.document_path,
                document_type=params.document_type or 'unknown',
                status='pending'
            )
        
        # Process document with LLM
        result = await process_document_with_llm(document.id)
        
        if result.get('success'):
            return {
                "success": True,
                "document_id": str(document.id),
                "document_type": result.get('document_type', 'unknown'),
                "extracted_data": result.get('extracted_data', {}),
                "transactions": result.get('transactions', []),
                "confidence": result.get('confidence', 0.0),
                "status": "processed"
            }
        else:
            return {
                "success": False,
                "error": result.get('error', 'Document processing failed'),
                "document_id": str(document.id)
            }
            
    except Exception as e:
        logger.error(f"Error in analyze_document_tool: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def generate_custom_report_tool(
    params: GenerateCustomReportParams
) -> Dict[str, Any]:
    """
    Generate a custom financial report based on natural language query.
    Uses AI to interpret the query and generate appropriate data.
    """
    try:
        from transactions.models import JournalEntry, JournalEntryLine
        from companies.models import ChartOfAccounts
        from datetime import datetime, timedelta
        from django.db.models import Sum, Count, Q
        
        # Parse dates
        if params.end_date:
            end_date = datetime.strptime(params.end_date, '%Y-%m-%d').date()
        else:
            end_date = datetime.now().date()
        
        if params.start_date:
            start_date = datetime.strptime(params.start_date, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=90)
        
        # Analyze query to determine report type
        query_lower = params.query.lower()
        
        # Revenue analysis
        if any(word in query_lower for word in ['receita', 'revenue', 'venda', 'sales']):
            accounts = ChartOfAccounts.objects.filter(
                company_id=params.company_id,
                account_type='REVENUE',
                is_active=True
            )
            
            data = []
            for account in accounts[:params.limit]:
                lines = JournalEntryLine.objects.filter(
                    account=account,
                    journal_entry__date__gte=start_date,
                    journal_entry__date__lte=end_date
                ).aggregate(
                    total=Sum('credit') - Sum('debit'),
                    count=Count('id')
                )
                
                if lines['total']:
                    data.append({
                        "account": account.name,
                        "code": account.code,
                        "total": float(lines['total']),
                        "transactions": lines['count']
                    })
            
            # Sort by total descending
            data.sort(key=lambda x: x['total'], reverse=True)
            
            return {
                "success": True,
                "report_type": "revenue_analysis",
                "query": params.query,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "data": data,
                "total": sum(item['total'] for item in data),
                "summary": f"Found {len(data)} revenue accounts with total of ${sum(item['total'] for item in data):,.2f}"
            }
        
        # Expense analysis
        elif any(word in query_lower for word in ['despesa', 'expense', 'gasto', 'cost']):
            accounts = ChartOfAccounts.objects.filter(
                company_id=params.company_id,
                account_type='EXPENSE',
                is_active=True
            )
            
            data = []
            for account in accounts[:params.limit]:
                lines = JournalEntryLine.objects.filter(
                    account=account,
                    journal_entry__date__gte=start_date,
                    journal_entry__date__lte=end_date
                ).aggregate(
                    total=Sum('debit') - Sum('credit'),
                    count=Count('id')
                )
                
                if lines['total']:
                    data.append({
                        "account": account.name,
                        "code": account.code,
                        "total": float(lines['total']),
                        "transactions": lines['count']
                    })
            
            # Sort by total descending
            data.sort(key=lambda x: x['total'], reverse=True)
            
            return {
                "success": True,
                "report_type": "expense_analysis",
                "query": params.query,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "data": data,
                "total": sum(item['total'] for item in data),
                "summary": f"Found {len(data)} expense accounts with total of ${sum(item['total'] for item in data):,.2f}"
            }
        
        # Top transactions
        elif any(word in query_lower for word in ['maior', 'top', 'largest', 'biggest']):
            entries = JournalEntry.objects.filter(
                company_id=params.company_id,
                date__gte=start_date,
                date__lte=end_date
            ).annotate(
                total_amount=Sum('lines__debit')
            ).order_by('-total_amount')[:params.limit]
            
            data = []
            for entry in entries:
                data.append({
                    "date": entry.date.isoformat(),
                    "description": entry.description,
                    "amount": float(entry.total_amount or 0),
                    "lines_count": entry.lines.count()
                })
            
            return {
                "success": True,
                "report_type": "top_transactions",
                "query": params.query,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "data": data,
                "summary": f"Top {len(data)} transactions found"
            }
        
        # Monthly summary
        elif any(word in query_lower for word in ['mensal', 'monthly', 'mês', 'month']):
            from django.db.models.functions import TruncMonth
            
            monthly_data = JournalEntryLine.objects.filter(
                journal_entry__company_id=params.company_id,
                journal_entry__date__gte=start_date,
                journal_entry__date__lte=end_date
            ).annotate(
                month=TruncMonth('journal_entry__date')
            ).values('month').annotate(
                total_debit=Sum('debit'),
                total_credit=Sum('credit'),
                count=Count('id')
            ).order_by('month')
            
            data = []
            for item in monthly_data:
                data.append({
                    "month": item['month'].strftime('%Y-%m'),
                    "debits": float(item['total_debit'] or 0),
                    "credits": float(item['total_credit'] or 0),
                    "transactions": item['count']
                })
            
            return {
                "success": True,
                "report_type": "monthly_summary",
                "query": params.query,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "data": data,
                "summary": f"Monthly data for {len(data)} months"
            }
        
        # Default: general query
        else:
            return {
                "success": False,
                "error": "Could not interpret query. Try keywords like 'revenue', 'expense', 'top', or 'monthly'",
                "query": params.query,
                "suggestions": [
                    "Show revenue by account",
                    "Top 10 largest expenses",
                    "Monthly transaction summary",
                    "Expense analysis for last quarter"
                ]
            }
            
    except Exception as e:
        logger.error(f"Error in generate_custom_report_tool: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": params.query
        }


def _find_duplicates(entries) -> List[Dict[str, Any]]:
    """Find potential duplicate transactions"""
    duplicates = []
    seen = {}
    
    for entry in entries:
        key = f"{entry.date}:{entry.description}:{entry.get_total_debit()}"
        
        if key in seen:
            duplicates.append({
                "type": "duplicate",
                "severity": "critical",
                "transaction_ids": [str(seen[key]), str(entry.id)],
                "description": f"Possible duplicate: '{entry.description}' on {entry.date}",
                "recommendation": "Review and remove duplicate if confirmed",
            })
        else:
            seen[key] = entry.id
    
    return duplicates


def _find_unusual_amounts(entries, company_id: str) -> List[Dict[str, Any]]:
    """Find transactions with unusual amounts"""
    from decimal import Decimal
    
    unusual = []
    
    # Calculate statistics by account
    account_stats = {}
    
    for entry in entries:
        for line in entry.lines.all():
            account_code = line.account.code
            amount = line.debit if line.debit else line.credit
            
            if account_code not in account_stats:
                account_stats[account_code] = []
            
            account_stats[account_code].append(float(amount))
    
    # Find outliers (> 3 standard deviations from mean)
    for entry in entries:
        for line in entry.lines.all():
            account_code = line.account.code
            amount = float(line.debit if line.debit else line.credit)
            
            if account_code in account_stats and len(account_stats[account_code]) > 10:
                values = account_stats[account_code]
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std_dev = variance ** 0.5
                
                if abs(amount - mean) > 3 * std_dev:
                    unusual.append({
                        "type": "unusual_amount",
                        "severity": "warning",
                        "transaction_id": str(entry.id),
                        "description": f"Amount ${amount:,.2f} is {abs(amount - mean) / std_dev:.1f}σ from mean for account {account_code}",
                        "recommendation": "Verify amount is correct",
                    })
    
    return unusual


def _find_inconsistencies(entries, company_id: str) -> List[Dict[str, Any]]:
    """Find classification inconsistencies"""
    inconsistencies = []
    
    # Group similar descriptions
    description_accounts = {}
    
    for entry in entries:
        desc = entry.description.lower()
        
        for line in entry.lines.all():
            if desc not in description_accounts:
                description_accounts[desc] = set()
            
            description_accounts[desc].add(line.account.code)
    
    # Find descriptions mapped to multiple accounts
    for desc, accounts in description_accounts.items():
        if len(accounts) > 2:  # Allow some variation
            inconsistencies.append({
                "type": "inconsistent_classification",
                "severity": "warning",
                "description": f"Description '{desc}' mapped to {len(accounts)} different accounts",
                "accounts": list(accounts),
                "recommendation": "Standardize classification for similar transactions",
            })
    
    return inconsistencies


# Tool registry
TOOL_REGISTRY = {
    "classify_transaction": {
        "function": classify_transaction_tool,
        "params": ClassifyTransactionParams,
        "description": "Classify a transaction using AI with historical context",
    },
    "create_journal_entry": {
        "function": create_journal_entry_tool,
        "params": CreateJournalEntryParams,
        "description": "Create a journal entry with double-entry validation",
    },
    "audit_transactions": {
        "function": audit_transactions_tool,
        "params": AuditTransactionsParams,
        "description": "Analyze transactions for anomalies and inconsistencies",
    },
    "analyze_document": {
        "function": analyze_document_tool,
        "params": AnalyzeDocumentParams,
        "description": "Analyze a document for key information extraction",
    },
    "generate_custom_report": {
        "function": generate_custom_report_tool,
        "params": GenerateCustomReportParams,
        "description": "Generate a custom report based on natural language query",
    },
}


async def execute_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool by name"""
    tool_config = TOOL_REGISTRY.get(tool_name)
    
    if not tool_config:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}",
        }
    
    try:
        # Validate params
        params_model = tool_config["params"](**params)
        
        # Execute tool
        result = await tool_config["function"](params_model)
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {
            "success": False,
            "error": str(e),
        }
