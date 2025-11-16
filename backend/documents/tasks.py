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

from .models import Document
from transactions.models import Transaction
from companies.models import ChartOfAccounts


@shared_task
def process_document(document_id):
    """
    Process uploaded document and extract transaction data.
    """
    try:
        document = Document.objects.get(id=document_id)
        document.status = 'PROCESSING'
        document.save()
        
        file_type = document.file_type.upper()
        
        if file_type == 'CSV':
            result = process_csv(document)
        elif file_type == 'PDF':
            result = process_pdf(document)
        elif file_type in ['JPG', 'JPEG', 'PNG']:
            result = process_image(document)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Save processing result
        document.processing_result = result
        document.status = 'COMPLETED'
        document.processed_date = timezone.now()
        document.save()
        
        # Create transactions from extracted data
        create_transactions_from_result(document, result)
        
        return {
            'status': 'success',
            'document_id': str(document_id),
            'transactions_created': result.get('transactions_count', 0)
        }
        
    except Document.DoesNotExist:
        return {'status': 'error', 'message': 'Document not found'}
    except Exception as e:
        # Mark document as failed
        try:
            document = Document.objects.get(id=document_id)
            document.status = 'FAILED'
            document.error_message = str(e)
            document.save()
        except:
            pass
        
        return {'status': 'error', 'message': str(e)}


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
        except:
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
            except Exception as e:
                # Skip problematic rows but continue processing
                print(f"Skipping row due to error: {e}")
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
            except:
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
            except:
                continue
    
    # Check for debit/credit columns
    debit = None
    credit = None
    
    for field in debit_fields:
        if field in row_lower and row_lower[field]:
            try:
                debit = parse_amount(row_lower[field])
                break
            except:
                continue
    
    for field in credit_fields:
        if field in row_lower and row_lower[field]:
            try:
                credit = parse_amount(row_lower[field])
                break
            except:
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


def extract_transactions_from_text(text):
    """Extract transactions from plain text using OpenAI API."""
    transactions = []
    
    if not text or not text.strip():
        return transactions
    
    try:
        import openai
        from django.conf import settings
        
        # Configure OpenAI
        openai.api_key = settings.OPENAI_API_KEY
        
        # Prepare prompt
        prompt = f"""Extract all financial transactions from the following text.
For each transaction, provide:
- date (YYYY-MM-DD format)
- description
- amount (positive for income/deposits, negative for expenses/withdrawals)
- category (if identifiable)

Text:
{text[:4000]}

Return ONLY a JSON array of transactions, no other text. Example format:
[{{"date": "2024-01-15", "description": "Grocery Store", "amount": -45.50, "category": "Groceries"}}]
"""
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial data extraction assistant. Extract transaction data and return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse response
        result_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        # Parse JSON
        transactions = json.loads(result_text)
        
        # Validate and clean transactions
        cleaned_transactions = []
        for trans in transactions:
            if 'date' in trans and 'amount' in trans:
                cleaned_transactions.append({
                    'date': trans['date'],
                    'description': trans.get('description', 'Transaction'),
                    'amount': float(trans['amount']),  # Convert to float for JSON serialization
                    'category': trans.get('category'),
                    'confidence': 0.8  # OpenAI extraction confidence
                })
        
        return cleaned_transactions
        
    except Exception as e:
        print(f"OpenAI extraction failed: {e}")
        # Fallback to pattern matching
        return extract_transactions_pattern_matching(text)


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
        except:
            continue
    
    return transactions


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
        except:
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
    except:
        return 0.0


def create_transactions_from_result(document, result):
    """Create Transaction objects from processing result."""
    transactions_data = result.get('transactions', [])
    
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
                suggested_category=trans_data.get('category', ''),  # Provide empty string if None
                confidence_score=trans_data.get('confidence', 0.5)
            )
        except Exception as e:
            # Log error but continue processing other transactions
            print(f"Error creating transaction: {e}")
            continue

