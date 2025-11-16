"""
Celery tasks for document processing.
"""
from celery import shared_task
from django.utils import timezone
import os
import json
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import csv
import io
from datetime import datetime
from decimal import Decimal
import logging
import traceback

from .models import Document
from .validators import TransactionValidator, LLMResponseValidator
from transactions.models import Transaction
from companies.models import ChartOfAccounts
from core.rag_service import rag_service

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document(self, document_id):
    """
    Process uploaded document and extract transaction data with improved error handling.
    """
    document = None
    try:
        document = Document.objects.get(id=document_id)
        logger.info(f"Starting processing for document {document_id}: {document.file_name}")
        
        # Update status to PROCESSING
        document.status = 'PROCESSING'
        document.update_progress('initializing', 5, 'Starting document processing')
        
        file_type = document.file_type.upper()
        
        # Process based on file type
        document.update_progress('extracting', 20, f'Extracting data from {file_type}')
        
        if file_type == 'CSV':
            result = process_csv(document)
        elif file_type == 'PDF':
            result = process_pdf(document)
        elif file_type in ['JPG', 'JPEG', 'PNG']:
            result = process_image(document)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Validate extracted transactions
        document.update_progress('validating', 60, 'Validating extracted transactions')
        transactions = result.get('transactions', [])
        
        if transactions:
            validation_result = TransactionValidator.validate_all_transactions(transactions)
            logger.info(f"Validation result: {validation_result['valid_count']}/{validation_result['total']} valid")
            
            result['validation'] = validation_result
            
            # Filter only valid transactions
            valid_transactions = [
                trans for trans in transactions
                if TransactionValidator.validate_extracted_transaction(trans)[0]
            ]
            result['transactions'] = valid_transactions
            result['transactions_count'] = len(valid_transactions)
        
        # Save extracted data for review
        document.update_progress('saving', 80, 'Saving extracted data')
        document.extracted_data = result
        document.processing_result = result
        document.status = 'READY_FOR_REVIEW'
        document.processed_date = timezone.now()
        document.save()
        
        document.update_progress('completed', 100, 'Processing completed successfully')
        
        logger.info(f"Document {document_id} processed successfully. {result.get('transactions_count', 0)} transactions extracted")
        
        return {
            'status': 'success',
            'document_id': str(document_id),
            'transactions_extracted': result.get('transactions_count', 0),
            'validation': result.get('validation', {})
        }
        
    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        return {'status': 'error', 'message': 'Document not found'}
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        logger.error(f"Error processing document {document_id}: {error_msg}\n{error_trace}")
        
        # Log error in document
        if document:
            document.log_error(error_msg, error_type=type(e).__name__)
            
            # Retry if possible
            if document.can_retry():
                logger.info(f"Retrying document {document_id} (attempt {document.processing_attempts + 1})")
                raise self.retry(exc=e, countdown=60)  # Retry after 1 minute
        
        return {'status': 'error', 'message': error_msg, 'trace': error_trace}


def process_csv(document):
    """Process CSV file and extract transactions."""
    transactions = []
    
    with open(document.file_path, 'r', encoding='utf-8') as file:
        # Read all lines first
        lines = file.readlines()
        
        # Skip empty lines and find the header line
        header_idx = -1
        for i, line in enumerate(lines):
            # A header line should have multiple comma-separated values
            if ',' in line and line.count(',') >= 2:
                # Check if it looks like a header (contains common field names)
                line_lower = line.lower()
                if any(field in line_lower for field in ['date', 'amount', 'description', 'transaction']):
                    header_idx = i
                    break
        
        if header_idx == -1:
            # No valid header found, return empty
            return {
                'format': 'CSV',
                'transactions': [],
                'transactions_count': 0,
                'raw_data': None
            }
        
        # Process CSV starting from header
        csv_content = ''.join(lines[header_idx:])
        csv_file = io.StringIO(csv_content)
        
        try:
            dialect = csv.Sniffer().sniff(csv_content[:1024])
            reader = csv.DictReader(csv_file, dialect=dialect)
        except (csv.Error, UnicodeDecodeError) as e:
            logger.warning(f"Failed to detect CSV dialect: {e}. Using default CSV reader.")
            csv_file.seek(0)
            reader = csv.DictReader(csv_file)
        except Exception as e:
            logger.error(f"Unexpected error processing CSV: {e}")
            csv_file.seek(0)
            reader = csv.DictReader(csv_file)
        
        for row in reader:
            try:
                # Skip rows that are clearly not data rows
                if not row or all(not v or str(v).strip() == '' for v in row.values()):
                    continue
                
                # Skip summary/total rows
                row_str = str(row).lower()
                if any(word in row_str for word in ['summary', 'total', 'subtotal', 'balance']):
                    continue
                
                # Try to extract transaction data
                transaction = extract_transaction_from_row(row)
                if transaction:
                    transactions.append(transaction)
            except (ValueError, KeyError, TypeError) as e:
                # Skip problematic rows but continue processing
                logger.warning(f"Skipping CSV row due to parsing error: {e}. Row data: {row}")
                continue
            except Exception as e:
                # Log unexpected errors but continue
                logger.error(f"Unexpected error processing CSV row: {e}. Row data: {row}")
                continue
    
    return {
        'format': 'CSV',
        'transactions': transactions,
        'transactions_count': len(transactions),
        'raw_data': None  # Don't store raw CSV data
    }


def process_pdf(document):
    """Process PDF file using pdfplumber and OCR if needed."""
    transactions = []
    text_content = ""
    
    try:
        # First try pdfplumber for text extraction
        with pdfplumber.open(document.file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content += text + "\n"
                
                # Try to extract tables
                tables = page.extract_tables()
                for table in tables:
                    transactions.extend(extract_transactions_from_table(table))
        
        # If no text was extracted, use OCR
        if not text_content.strip():
            text_content = ocr_pdf(document.file_path)
            transactions.extend(extract_transactions_from_text(text_content))
        
    except Exception as e:
        # Fallback to OCR
        text_content = ocr_pdf(document.file_path)
        transactions.extend(extract_transactions_from_text(text_content))
    
    return {
        'format': 'PDF',
        'text_content': text_content[:5000],  # Limit stored text
        'transactions': transactions,
        'transactions_count': len(transactions)
    }


def process_image(document):
    """Process image file using OCR."""
    try:
        image = Image.open(document.file_path)
        text_content = pytesseract.image_to_string(image)
        
        transactions = extract_transactions_from_text(text_content)
        
        return {
            'format': 'IMAGE',
            'text_content': text_content[:5000],
            'transactions': transactions,
            'transactions_count': len(transactions)
        }
    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")


def ocr_pdf(file_path):
    """Convert PDF to images and perform OCR."""
    text_content = ""
    
    try:
        # Convert PDF to images
        images = convert_from_path(file_path, dpi=300)
        
        # Perform OCR on each page
        for image in images:
            text = pytesseract.image_to_string(image)
            text_content += text + "\n"
    except Exception as e:
        raise Exception(f"PDF OCR failed: {str(e)}")
    
    return text_content


def extract_transaction_from_row(row):
    """Extract transaction data from CSV row."""
    # Common field names
    date_fields = ['date', 'transaction date', 'posting date', 'trans date']
    desc_fields = ['description', 'memo', 'details', 'payee']
    amount_fields = ['amount', 'total', 'value']
    debit_fields = ['debit', 'withdrawal', 'payment']
    credit_fields = ['credit', 'deposit', 'income']
    
    # Normalize keys to lowercase (handle None keys)
    row_lower = {str(k).lower().strip() if k else '': v for k, v in row.items()}
    
    transaction = {}
    
    # Extract date
    for field in date_fields:
        if field in row_lower and row_lower[field]:
            try:
                transaction['date'] = parse_date(row_lower[field])
                break
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse date from field '{field}': {row_lower[field]}. Error: {e}")
                continue
    
    # Extract description
    for field in desc_fields:
        if field in row_lower and row_lower[field]:
            transaction['description'] = row_lower[field]
            break
    
    # Extract amount
    amount = None
    for field in amount_fields:
        if field in row_lower and row_lower[field]:
            try:
                amount = parse_amount(row_lower[field])
                break
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse amount from field '{field}': {row_lower[field]}. Error: {e}")
                continue
    
    # Check for debit/credit columns
    debit = None
    credit = None
    
    for field in debit_fields:
        if field in row_lower and row_lower[field]:
            try:
                debit = parse_amount(row_lower[field])
                break
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse debit from field '{field}': {row_lower[field]}. Error: {e}")
                continue
    
    for field in credit_fields:
        if field in row_lower and row_lower[field]:
            try:
                credit = parse_amount(row_lower[field])
                break
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse credit from field '{field}': {row_lower[field]}. Error: {e}")
                continue
    
    # Determine final amount
    if debit and credit:
        transaction['amount'] = credit - debit
    elif debit:
        transaction['amount'] = -abs(debit)
    elif credit:
        transaction['amount'] = abs(credit)
    elif amount:
        transaction['amount'] = amount
    
    # Only return if we have minimum required fields
    if 'date' in transaction and 'amount' in transaction:
        if 'description' not in transaction:
            transaction['description'] = 'Transaction'
        return transaction
    
    return None


def extract_transactions_from_table(table):
    """Extract transactions from PDF table."""
    transactions = []
    
    if not table or len(table) < 2:
        return transactions
    
    # Assume first row is header
    headers = [str(h).lower().strip() if h else '' for h in table[0]]
    
    for row in table[1:]:
        if not row:
            continue
        
        # Create dict from headers and row
        row_dict = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
        
        transaction = extract_transaction_from_row(row_dict)
        if transaction:
            transactions.append(transaction)
    
    return transactions


def extract_transactions_pattern_matching(text):
    """Fallback: Extract transactions using regex patterns."""
    import re
    transactions = []
    
    # Pattern for date + amount + description
    # Example: "01/15/2024 $45.50 Grocery Store"
    pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+\$?([\d,]+\.\d{2})\s+(.+?)(?=\n|$)'
    
    matches = re.findall(pattern, text, re.MULTILINE)
    
    for match in matches:
        try:
            date_str, amount_str, description = match
            transactions.append({
                'date': parse_date(date_str),
                'description': description.strip(),
                'amount': parse_amount(amount_str),
                'confidence': 0.5  # Lower confidence for pattern matching
            })
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse transaction from text pattern: {match}. Error: {e}")
            continue
    
    return transactions


def extract_transactions_from_text(text):
    """Extract transactions from plain text using Manus LLM API (OpenAI-compatible)."""
    transactions = []
    
    if not text or not text.strip():
        return transactions
    
    try:
        from openai import OpenAI
        from django.conf import settings
        
        logger.info("Starting LLM-based transaction extraction with RAG")
        
        # Initialize Manus API client (OpenAI-compatible)
        client = OpenAI()
        
        # Create improved prompt with few-shot examples
        prompt = LLMResponseValidator.create_improved_prompt(text, max_length=4000)
        
        # Call Manus API (OpenAI-compatible)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # Manus model: fast and efficient
            messages=[
                {
                    "role": "system", 
                    "content": "You are a financial data extraction assistant. Extract transaction data and return ONLY a valid JSON array, no other text or explanation."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )
        
        # Parse response
        result_text = response.choices[0].message.content.strip()
        logger.info(f"LLM returned response of length: {len(result_text)}")
        
        # Validate and parse LLM response
        validated_transactions = LLMResponseValidator.validate_llm_json_response(result_text)
        
        if validated_transactions is None:
            logger.warning("LLM response validation failed, falling back to pattern matching")
            return extract_transactions_pattern_matching(text)
        
        # Clean and normalize transactions
        cleaned_transactions = []
        for trans in validated_transactions:
            if 'date' in trans and 'amount' in trans:
                cleaned_transactions.append({
                    'date': trans['date'],
                    'description': trans.get('description', 'Transaction'),
                    'amount': float(trans['amount']),
                    'category': trans.get('category', ''),
                    'vendor': trans.get('vendor', ''),
                    'confidence': trans.get('confidence', 0.8)
                })
        
        logger.info(f"Successfully extracted {len(cleaned_transactions)} transactions via LLM")
        return cleaned_transactions
        
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}", exc_info=True)
        # Fallback to pattern matching
        return extract_transactions_pattern_matching(text)


def extract_transactions_with_rag(text, company_id):
    """
    Extract and classify transactions using RAG for better context.
    
    Args:
        text: Raw text from document
        company_id: Company ID for context retrieval
        
    Returns:
        List of transactions with RAG-enhanced classification
    """
    # First extract basic transaction data
    transactions = extract_transactions_from_text(text)
    
    if not transactions:
        return transactions
    
    logger.info(f"Enhancing {len(transactions)} transactions with RAG")
    
    # Enhance each transaction with RAG
    enhanced_transactions = []
    for trans in transactions:
        try:
            # Generate embedding for transaction
            transaction_data = {
                'description': trans.get('description', ''),
                'vendor': trans.get('vendor', ''),
                'amount': trans.get('amount', 0),
                'category': trans.get('category', '')
            }
            
            # Use RAG to find similar transactions and get context
            augmented_prompt = rag_service.augment_prompt_with_context(
                transaction_data,
                company_id,
                max_examples=5
            )
            
            # If RAG found similar transactions, use them to improve classification
            embedding = rag_service.generate_transaction_embedding(transaction_data)
            
            if embedding:
                similar = rag_service.find_similar_transactions(
                    embedding,
                    company_id,
                    top_k=3,
                    min_similarity=0.75
                )
                
                if similar:
                    # Use the most similar transaction's account
                    best_match = similar[0]
                    trans['suggested_account_code'] = best_match['account_code']
                    trans['suggested_account_name'] = best_match['account_name']
                    trans['rag_confidence'] = best_match['similarity']
                    trans['confidence'] = max(trans.get('confidence', 0.5), best_match['similarity'])
                    logger.info(f"RAG matched '{trans['description']}' with {best_match['similarity']:.2%} confidence")
            
            enhanced_transactions.append(trans)
            
        except Exception as e:
            logger.error(f"RAG enhancement failed for transaction: {e}")
            enhanced_transactions.append(trans)  # Use original if RAG fails
    
    return enhanced_transactions


def parse_date(date_str):
    """Parse date string to YYYY-MM-DD format."""
    date_str = str(date_str).strip()
    
    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%m-%d-%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%b %d, %Y',
        '%B %d, %Y',
        '%d %b %Y',
        '%d %B %Y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            # Try next format
            continue
    
    raise ValueError(f"Could not parse date: {date_str}")


def parse_amount(amount_str):
    """Parse amount string to float."""
    if not amount_str:
        return 0.0
    
    # Remove currency symbols and whitespace
    amount_str = str(amount_str).strip()
    amount_str = amount_str.replace('$', '').replace('€', '').replace('£', '')
    amount_str = amount_str.replace(',', '').replace(' ', '')
    
    # Handle parentheses as negative
    if '(' in amount_str and ')' in amount_str:
        amount_str = amount_str.replace('(', '-').replace(')', '')
    
    try:
        return float(amount_str)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse amount '{amount_str}': {e}. Returning 0.0")
        return 0.0


def create_transactions_from_result(document, result):
    """
    Create Transaction objects from processing result.
    Note: This function is now called explicitly after user review.
    """
    transactions_data = result.get('transactions', [])
    created_count = 0
    
    for trans_data in transactions_data:
        try:
            # Get amount and ensure it's positive (constraint requires amount >= 0)
            amount = trans_data.get('amount', 0)
            amount = abs(float(amount))  # Convert to absolute value
            
            Transaction.objects.create(
                company=document.company,
                document=document,
                date=trans_data.get('date'),
                description=trans_data.get('description', 'Extracted transaction'),
                amount=amount,
                is_validated=False,
                suggested_category=trans_data.get('category', ''),
                confidence_score=trans_data.get('confidence', 0.5)
            )
            created_count += 1
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            continue
    
    logger.info(f"Created {created_count} transactions from document {document.id}")
    return created_count

