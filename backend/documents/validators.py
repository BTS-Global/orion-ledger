"""
Validators for document processing and transaction extraction.
"""
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import logging
import jsonschema
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class TransactionValidator:
    """Validator for extracted transactions"""
    
    @staticmethod
    def validate_extracted_transaction(trans_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate an extracted transaction
        
        Args:
            trans_data: Dictionary with transaction data
            
        Returns:
            tuple: (is_valid, list of error messages)
        """
        errors = []
        
        # Validate date
        if 'date' not in trans_data or not trans_data['date']:
            errors.append("Date is required")
        else:
            if not TransactionValidator._validate_date(trans_data['date']):
                errors.append("Date format is invalid. Expected YYYY-MM-DD")
        
        # Validate amount
        if 'amount' not in trans_data or trans_data['amount'] is None:
            errors.append("Amount is required")
        else:
            if not TransactionValidator._validate_amount(trans_data['amount']):
                errors.append("Amount must be a valid number")
        
        # Validate description
        if 'description' not in trans_data or not trans_data['description']:
            errors.append("Description is required")
        elif len(str(trans_data['description']).strip()) < 3:
            errors.append("Description must be at least 3 characters")
        
        # Validate type (if present)
        if 'type' in trans_data and trans_data['type']:
            if str(trans_data['type']).upper() not in ['DEBIT', 'CREDIT']:
                errors.append("Type must be 'debit' or 'credit'")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_date(date_str: str) -> bool:
        """Validate date format"""
        try:
            datetime.strptime(str(date_str), '%Y-%m-%d')
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _validate_amount(amount) -> bool:
        """Validate that amount is numeric"""
        try:
            Decimal(str(amount))
            return True
        except (InvalidOperation, ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_all_transactions(transactions: List[Dict]) -> Dict:
        """
        Validate a list of transactions
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            dict: {
                'valid_count': int,
                'invalid_count': int,
                'total': int,
                'errors': List[Dict]
            }
        """
        valid_count = 0
        invalid_count = 0
        errors = []
        
        for idx, trans in enumerate(transactions):
            is_valid, trans_errors = TransactionValidator.validate_extracted_transaction(trans)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                errors.append({
                    'transaction_index': idx,
                    'transaction': trans,
                    'errors': trans_errors
                })
        
        return {
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'total': len(transactions),
            'errors': errors
        }


class LLMResponseValidator:
    """Validator for LLM responses"""
    
    # JSON Schema for transaction extraction
    TRANSACTION_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
                "description": {"type": "string", "minLength": 1},
                "amount": {"type": ["number", "string"]},
                "type": {"type": "string"},
                "category": {"type": "string"},
                "vendor": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["date", "description", "amount"]
        }
    }
    
    @staticmethod
    def validate_llm_json_response(response_text: str) -> Optional[List[Dict]]:
        """
        Validate and extract JSON from LLM response
        
        Args:
            response_text: Text response from LLM
            
        Returns:
            Validated list of transactions or None if invalid
        """
        try:
            # Clean markdown code blocks if present
            cleaned_text = LLMResponseValidator._clean_markdown(response_text)
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            # Ensure data is a list
            if not isinstance(data, list):
                logger.error("LLM response is not a list")
                return None
            
            # Validate schema
            validate(instance=data, schema=LLMResponseValidator.TRANSACTION_SCHEMA)
            
            logger.info(f"LLM response validated successfully. Found {len(data)} transactions")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from LLM: {e}")
            return None
        except ValidationError as e:
            logger.error(f"Schema validation failed: {e.message}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error validating LLM response: {e}")
            return None
    
    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Remove markdown code blocks from text"""
        text = text.strip()
        
        # Remove ```json or ``` at the beginning
        if text.startswith('```'):
            lines = text.split('\n')
            # Remove first line (```json or ```)
            if lines[0].strip() in ['```json', '```', '```JSON']:
                lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            text = '\n'.join(lines)
        
        return text.strip()
    
    @staticmethod
    def create_improved_prompt(text: str, company_name: str = "", max_length: int = 4000) -> str:
        """
        Create improved prompt for transaction extraction with few-shot examples
        
        Args:
            text: Extracted text from document
            company_name: Company name for context
            max_length: Maximum text length to include
            
        Returns:
            Formatted prompt
        """
        # Truncate text if too long
        truncated_text = text[:max_length] if len(text) > max_length else text
        
        prompt = f"""You are an expert financial data extraction assistant. Extract ALL financial transactions from the document text below.

{"Company: " + company_name if company_name else ""}

INSTRUCTIONS:
1. Extract EVERY transaction you can identify
2. Use YYYY-MM-DD format for dates (if year is missing, use 2024)
3. Extract numeric values only for amounts (no currency symbols)
4. Make amount positive for income/deposits, negative for expenses/withdrawals
5. Provide clear descriptions
6. Include category if identifiable (e.g., "Office Supplies", "Rent", "Sales")
7. Return ONLY a valid JSON array, no other text

EXAMPLE OUTPUT FORMAT:
[
  {{"date": "2024-01-15", "description": "Office Depot - Supplies", "amount": -45.50, "category": "Office Supplies", "confidence": 0.9}},
  {{"date": "2024-01-16", "description": "Client Payment - Invoice #123", "amount": 1500.00, "category": "Revenue", "confidence": 0.95}}
]

DOCUMENT TEXT:
{truncated_text}

Return ONLY the JSON array of transactions:"""
        
        return prompt
