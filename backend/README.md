# Accounting Software for US Companies

A fullstack accounting software designed for US companies, featuring automated document processing, IRS form generation, and comprehensive financial reporting.

## Features

- **Multi-Company Management**: Manage accounting for multiple companies from a single account
- **Document Processing**: Upload and extract data from bank statements (PDF, CSV, images)
- **Intelligent Categorization**: AI-powered transaction categorization using OpenAI
- **Financial Reports**: Generate Balance Sheet, Income Statement, and Cash Flow Statement
- **IRS Forms**: Automatically generate Forms 5472, 1099, 1120, and 1040
- **Double-Entry Bookkeeping**: Full journal entry support
- **Audit Trail**: Complete history of all actions

## Tech Stack

### Backend
- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.16
- **Database**: PostgreSQL 14
- **Task Queue**: Celery + Redis
- **Documentation**: drf-spectacular (OpenAPI/Swagger)

### Frontend (Coming in Phase 6)
- **Framework**: Vue.js 3
- **UI Library**: Vuetify / Element Plus
- **State Management**: Pinia

### Key Libraries
- **Document Processing**: pdfplumber, pytesseract, pdf2image
- **AI**: OpenAI API
- **IRS Forms**: PyPDFForm
- **Reports**: openpyxl, WeasyPrint

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Setup

1. **Clone the repository**
```bash
cd /home/ubuntu/accounting_software
```

2. **Install dependencies**
```bash
pip3 install django djangorestframework django-cors-headers psycopg2-binary celery redis django-celery-beat drf-spectacular PyPDFForm pdfplumber pytesseract pdf2image openai python-dotenv pillow
```

3. **Configure environment variables**
Create a `.env` file with:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=accounting_db
DB_USER=accounting_user
DB_PASSWORD=accounting_pass123
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-api-key
```

4. **Setup database**
```bash
# Create PostgreSQL database and user
sudo -u postgres psql -c "CREATE DATABASE accounting_db;"
sudo -u postgres psql -c "CREATE USER accounting_user WITH PASSWORD 'accounting_pass123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE accounting_db TO accounting_user;"
sudo -u postgres psql -c "ALTER DATABASE accounting_db OWNER TO accounting_user;"

# Run migrations
python3.11 manage.py migrate
```

5. **Create superuser**
```bash
python3.11 manage.py createsuperuser
```

6. **Run the development server**
```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

7. **Start Celery worker (in a separate terminal)**
```bash
celery -A backend worker -l info
```

## API Documentation

Once the server is running, access the API documentation at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## API Endpoints

### Companies
- `GET /api/companies/` - List all companies
- `POST /api/companies/` - Create a new company
- `GET /api/companies/{id}/` - Get company details
- `PUT /api/companies/{id}/` - Update company
- `DELETE /api/companies/{id}/` - Delete company
- `POST /api/companies/{id}/activate/` - Set as active company

### Chart of Accounts
- `GET /api/accounts/` - List accounts
- `POST /api/accounts/` - Create account
- `GET /api/accounts/{id}/` - Get account details
- `PUT /api/accounts/{id}/` - Update account
- `DELETE /api/accounts/{id}/` - Delete account

### Documents
- `GET /api/documents/` - List documents
- `POST /api/documents/upload/` - Upload document
- `GET /api/documents/{id}/` - Get document details
- `GET /api/documents/{id}/status_check/` - Check processing status

### Transactions
- `GET /api/transactions/` - List transactions
- `GET /api/transactions/pending/` - List unvalidated transactions
- `POST /api/transactions/{id}/validate_transaction/` - Validate transaction
- `PUT /api/transactions/{id}/` - Update transaction
- `DELETE /api/transactions/{id}/` - Delete transaction

### Journal Entries
- `GET /api/journal-entries/` - List journal entries
- `POST /api/journal-entries/` - Create journal entry
- `GET /api/journal-entries/{id}/` - Get entry details

## Database Models

### Company
- Multi-company support with owner and shared users
- Fiscal year configuration
- Complete address and contact information

### UserProfile
- Extended user information
- Active company tracking

### ChartOfAccounts
- Customizable account structure
- Account types: Asset, Liability, Equity, Revenue, Expense
- IRS form box mapping
- Parent-child account relationships

### Document
- File upload tracking
- Processing status (Uploaded, Processing, Completed, Failed)
- Support for PDF, CSV, JPG, PNG

### Transaction
- Financial transaction records
- AI-suggested categorization
- Validation workflow
- Link to source document

### JournalEntry & JournalEntryLine
- Double-entry bookkeeping
- Automatic balance validation

### AuditLog
- Complete audit trail
- Immutable records

## Development Status

### ✅ Phase 1: Infrastructure and Data Models (COMPLETED)
- [x] Django project setup
- [x] PostgreSQL database configuration
- [x] All models created and migrated
- [x] REST API with DRF
- [x] API documentation with Swagger
- [x] Celery and Redis configuration
- [x] Django Admin configuration

### 🔄 Phase 2: Authentication and User Management (NEXT)
- [ ] OAuth integration (Google + Microsoft)
- [ ] User profile management
- [ ] Multi-company switching
- [ ] Frontend Vue.js setup

### 📋 Phase 3: Document Upload and Data Extraction
- [ ] File upload endpoint
- [ ] OCR processing
- [ ] AI-powered data extraction
- [ ] Validation interface

### 📋 Phase 4: Accounting Logic and Reports
- [ ] Double-entry conversion
- [ ] Balance Sheet generation
- [ ] Income Statement generation
- [ ] Cash Flow Statement generation
- [ ] PDF/Excel export

### 📋 Phase 5: IRS Form Generation
- [ ] Form 5472 generation
- [ ] Form 1099 generation
- [ ] Form 1120 generation
- [ ] Form 1040 generation

### 📋 Phase 6: Frontend Integration and UI/UX
- [ ] Complete Vue.js frontend
- [ ] Dashboard
- [ ] All screens integrated

### 📋 Phase 7: Testing, Deploy and Documentation
- [ ] Unit tests
- [ ] Integration tests
- [ ] Production deployment
- [ ] User manual

## Admin Access

- **URL**: http://localhost:8000/admin/
- **Username**: admin
- **Password**: admin123

## License

Proprietary - All rights reserved

## Support

For support, please contact the development team.

