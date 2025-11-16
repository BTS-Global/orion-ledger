# Orion Ledger

**Modern accounting system for US companies with AI-powered document processing and IRS form generation.**

> **Monorepo Structure:** This repository contains both the Django backend and React frontend in a unified codebase.

## 🚀 Features

### Core Functionality
- **Multi-company management** with double-entry bookkeeping
- **Chart of Accounts** with balance calculation and AI analysis
- **Transaction management** with journal entries
- **Document processing** with OCR and AI extraction
- **Financial reports** (Balance Sheet, Income Statement, Cash Flow)
- **IRS Forms generation** (1120, 5472, 1099-NEC, 1040)

### AI-Powered Features
- **Intelligent document extraction** - Upload receipts, invoices, bank statements and automatically extract transactions
- **Chart of Accounts analysis** - AI analyzes your accounts and suggests improvements
- **IRS Forms assistance** - AI reads official IRS instructions and helps fill forms correctly
- **Smart categorization** - Automatic transaction categorization based on your chart of accounts

### Dashboard & Analytics
- **KPI Cards** - Revenue, Expenses, Profit, Cash Runway
- **Interactive charts** - Revenue & Expenses trends (12 months)
- **Expense breakdown** - Pie chart with top 5 categories
- **Cash runway indicator** - Visual alerts (green/yellow/red)

## 📁 Monorepo Structure

```
orion-ledger/
├── backend/               # Django Backend
│   ├── backend/          # Django settings and configuration
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── wsgi.py
│   ├── companies/        # Companies and Chart of Accounts
│   ├── core/             # Authentication and core functionality
│   ├── documents/        # Document upload and AI processing
│   ├── irs_forms/        # IRS Forms generation
│   ├── reports/          # Financial reports
│   ├── transactions/     # Transactions and journal entries
│   ├── manage.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/             # React Frontend
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── contexts/    # React contexts
│   │   └── config/      # Configuration
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
│
├── docs/                 # Documentation
└── examples/             # Example files and PDFs
```

## 🛠️ Tech Stack

### Backend
- **Django 4.2** with Django REST Framework
- **PostgreSQL** for database
- **Redis** for caching and Celery
- **Celery** for background tasks
- **OpenAI API** (via Manus) for AI features
- **PyPDF2** for PDF processing

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Recharts** for data visualization
- **Wouter** for routing

## 🚀 Quick Start

### Prerequisites
- **Node.js** 22+
- **Python** 3.11+
- **PostgreSQL** 14+
- **Redis** 7+

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver 8000

# In another terminal, run Celery worker
celery -A backend worker -l info
```

**Backend API:** `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Frontend:** `http://localhost:3001`

## 📊 Database Schema

### Core Models
- **Company** - Multi-company support
- **ChartOfAccounts** - Account structure (Assets, Liabilities, Equity, Revenue, Expenses)
- **Transaction** - Financial transactions
- **JournalEntry** - Double-entry bookkeeping
- **JournalEntryLine** - Debit/Credit lines
- **Document** - Uploaded documents with AI processing

## 🤖 AI Features

All AI features use **Manus LLM API** with free tokens:

### 1. Document Extraction
- Upload bank statements, receipts, invoices
- AI extracts transactions automatically
- Categorizes based on your Chart of Accounts
- Creates double-entry journal entries

### 2. Chart of Accounts Analysis
- Analyzes account structure
- Detects inconsistencies
- Suggests improvements
- Recommends missing accounts
- Provides health score (0-100)

### 3. IRS Forms Generation
- Downloads official IRS forms
- Reads and understands instructions
- Extracts financial data from system
- Validates calculations
- Generates professional PDF

## 📈 Performance

- **Dashboard load:** < 2s
- **API KPIs (cached):** < 100ms
- **Document processing:** 2-5s per document
- **AI analysis:** 30-60s

## 🔐 Security

- CSRF protection enabled
- CORS configured for production
- Environment variables for secrets
- SQL injection protection (Django ORM)
- XSS protection (React)

## 📝 API Documentation

API documentation available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## 🧪 Testing

### Backend
```bash
cd backend
python manage.py test
```

### Frontend
```bash
cd frontend
npm run test
```

## 📦 Deployment

### Backend (Railway/Heroku/AWS)
```bash
cd backend
# Set environment variables
# Run migrations
python manage.py migrate
# Collect static files
python manage.py collectstatic --noinput
```

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy dist/ folder
```

## 🌟 Recent Updates

### Monorepo Unification (November 2025)
- ✅ Unified `contabilidade-backend` and `orion-ledger` repositories
- ✅ Clean structure with `/backend` and `/frontend` directories
- ✅ No versioning conflicts (v2, old, legacy files removed)
- ✅ Complete documentation for both backend and frontend
- ✅ Standardized development workflow

### Version 1.1 (October 2025)

**Phase 1: Polish & Performance** ✅
- Dashboard with KPIs and interactive charts
- Tooltips and help text throughout the app
- Improved loading states and empty states
- Optimized queries with caching

**AI Features** ✅
- Document extraction with AI classification
- Chart of Accounts analysis
- IRS Forms generation with PDF output

**Documents Page Overhaul** ✅
- Fixed "View Document" 404 error
- Fixed "Invalid Date" display
- Added delete confirmation dialog
- Removed duplicate documents
- Added filters (search, status, type)
- Added pagination (10 per page)
- Improved design with icons and colors
- Better UX with empty states and toasts

**Chart of Accounts** ✅
- Fixed balance calculation
- Added company name display
- Optimized queries (< 200ms)

## 📚 Documentation

See `/docs` folder for detailed documentation:
- Implementation guides
- Roadmap
- Feature specifications
- API documentation

See also:
- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with ❤️ for US companies
- AI powered by Manus LLM API
- UI components by shadcn/ui
- Icons by Lucide

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/BTS-Global/orion-ledger/issues)
- Email: support@orionledger.com

---

**Status:** ✅ Production Ready  
**Version:** 1.1.0  
**Last Updated:** November 16, 2025
