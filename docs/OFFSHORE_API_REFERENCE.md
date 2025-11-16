# Offshore API Reference

**Base URL:** `/api/offshore/`

Todas as rotas requerem autenticação (token JWT ou session-based).

---

## 📋 Annual Returns

### List Annual Returns
```
GET /api/offshore/annual-returns/
```

**Query Parameters:**
- `company` - Filter by company ID
- `filing_year` - Filter by filing year
- `status` - Filter by status (DRAFT, PENDING, APPROVED, FILED, REJECTED)
- `search` - Search in company name or reference number
- `ordering` - Order by fields (e.g., `-filing_year`, `due_date`)

**Response:**
```json
[
  {
    "id": "uuid",
    "company": "uuid",
    "company_name": "Caribbean Trading Ltd",
    "company_jurisdiction": "BVI",
    "filing_year": 2024,
    "due_date": "2025-05-31",
    "filed_date": null,
    "status": "PENDING",
    "is_overdue": false
  }
]
```

### Create Annual Return
```
POST /api/offshore/annual-returns/
```

**Request Body:**
```json
{
  "company": "uuid",
  "filing_year": 2024,
  "due_date": "2025-05-31",
  "status": "DRAFT",
  "total_assets": 250000.00,
  "total_liabilities": 50000.00,
  "total_equity": 200000.00,
  "net_income": 75000.00,
  "notes": "Auto-generated from financial data"
}
```

### Get Overdue Annual Returns
```
GET /api/offshore/annual-returns/overdue/
```

**Query Parameters:**
- `company` - Filter by company ID (optional)

### Get Upcoming Annual Returns
```
GET /api/offshore/annual-returns/upcoming/
```

Returns annual returns due in the next 60 days.

### Generate PDF
```
POST /api/offshore/annual-returns/{id}/generate-pdf/
```

**Response:**
```json
{
  "message": "PDF generation is not yet implemented",
  "id": "uuid"
}
```

---

## 🏢 Economic Substance Reports

### List ES Reports
```
GET /api/offshore/es-reports/
```

**Query Parameters:**
- `company` - Filter by company ID
- `reporting_year` - Filter by reporting year
- `status` - Filter by status
- `business_activity` - Filter by business activity type
- `meets_substance_requirements` - Filter by compliance (true/false)

**Response:**
```json
[
  {
    "id": "uuid",
    "company": "uuid",
    "company_name": "Caribbean Trading Ltd",
    "company_jurisdiction": "BVI",
    "reporting_year": 2024,
    "submission_deadline": "2025-06-30",
    "business_activity": "HOLDING",
    "business_activity_display": "Holding Company Business",
    "meets_substance_requirements": true,
    "status": "DRAFT"
  }
]
```

### Create ES Report
```
POST /api/offshore/es-reports/
```

**Request Body:**
```json
{
  "company": "uuid",
  "reporting_year": 2024,
  "submission_deadline": "2025-06-30",
  "business_activity": "HOLDING",
  "activity_description": "Pure equity holding company",
  "has_adequate_employees": true,
  "num_employees": 2,
  "has_adequate_premises": true,
  "premises_address": "Registered office address",
  "has_adequate_expenditure": true,
  "annual_expenditure": 50000.00,
  "conducts_core_activities": true,
  "is_pure_equity_holding": true,
  "meets_reduced_substance": true
}
```

### Assess Compliance
```
POST /api/offshore/es-reports/{id}/assess/
```

Auto-assesses whether substance requirements are met based on provided data.

**Response:**
```json
{
  "meets_requirements": true,
  "assessment": {
    "has_adequate_employees": true,
    "has_adequate_premises": true,
    "has_adequate_expenditure": true,
    "conducts_core_activities": true
  },
  "message": "Assessment completed"
}
```

---

## 💰 Jurisdiction Fees

### List Fees
```
GET /api/offshore/fees/
```

**Query Parameters:**
- `company` - Filter by company ID
- `fee_type` - Filter by fee type
- `status` - Filter by status (PENDING, PAID, OVERDUE, WAIVED)
- `currency` - Filter by currency

**Response:**
```json
[
  {
    "id": "uuid",
    "company": "uuid",
    "company_name": "Caribbean Trading Ltd",
    "company_jurisdiction": "BVI",
    "fee_type": "ANNUAL_RENEWAL",
    "fee_type_display": "Annual Renewal Fee",
    "description": "Annual company renewal 2025",
    "amount": 1500.00,
    "currency": "USD",
    "due_date": "2025-01-15",
    "paid_date": null,
    "status": "PENDING",
    "status_display": "Pending Payment",
    "payment_reference": "",
    "is_overdue": false
  }
]
```

### Create Fee
```
POST /api/offshore/fees/
```

**Request Body:**
```json
{
  "company": "uuid",
  "fee_type": "ANNUAL_RENEWAL",
  "description": "Annual company renewal 2025",
  "amount": 1500.00,
  "currency": "USD",
  "due_date": "2025-01-15",
  "status": "PENDING"
}
```

### Get Overdue Fees
```
GET /api/offshore/fees/overdue/
```

**Query Parameters:**
- `company` - Filter by company ID (optional)

### Get Upcoming Fees
```
GET /api/offshore/fees/upcoming/
```

Returns fees due in the next 30 days.

### Mark as Paid
```
POST /api/offshore/fees/{id}/mark-paid/
```

**Request Body:**
```json
{
  "paid_date": "2025-01-10",
  "payment_reference": "TXN-12345"
}
```

---

## 💱 Exchange Rates

### List Exchange Rates
```
GET /api/offshore/exchange-rates/
```

**Query Parameters:**
- `from_currency` - Filter by from currency (e.g., USD)
- `to_currency` - Filter by to currency (e.g., EUR)
- `date` - Filter by date
- `source` - Filter by source

**Response:**
```json
[
  {
    "id": "uuid",
    "from_currency": "USD",
    "to_currency": "EUR",
    "rate": 0.920000,
    "date": "2025-11-16",
    "source": "manual",
    "created_at": "2025-11-16T10:00:00Z"
  }
]
```

### Create Exchange Rate
```
POST /api/offshore/exchange-rates/
```

**Request Body:**
```json
{
  "from_currency": "USD",
  "to_currency": "EUR",
  "rate": 0.92,
  "date": "2025-11-16",
  "source": "manual"
}
```

### Convert Currency
```
POST /api/offshore/exchange-rates/convert/
```

**Request Body:**
```json
{
  "amount": 1000.00,
  "from_currency": "USD",
  "to_currency": "EUR",
  "date": "2025-11-16"
}
```

**Response:**
```json
{
  "amount": 1000.00,
  "from_currency": "USD",
  "to_currency": "EUR",
  "converted_amount": 920.00,
  "rate": 0.920000,
  "date": "2025-11-16"
}
```

### Get Latest Rate
```
GET /api/offshore/exchange-rates/latest/?from_currency=USD&to_currency=EUR
```

**Response:**
```json
{
  "id": "uuid",
  "from_currency": "USD",
  "to_currency": "EUR",
  "rate": 0.920000,
  "date": "2025-11-16",
  "source": "manual",
  "created_at": "2025-11-16T10:00:00Z"
}
```

---

## 👥 Corporate Service Clients

### List Clients
```
GET /api/offshore/clients/
```

**Query Parameters:**
- `client_type` - Filter by client type (INDIVIDUAL, COMPANY, TRUST, FOUNDATION)
- `status` - Filter by status (PROSPECT, ACTIVE, INACTIVE, TERMINATED)
- `risk_rating` - Filter by risk rating (LOW, MEDIUM, HIGH)
- `kyc_completed` - Filter by KYC completion (true/false)
- `search` - Search in client reference, name, or email

**Response (list view):**
```json
[
  {
    "id": "uuid",
    "client_reference": "CLI-001",
    "client_name": "John Doe",
    "client_type": "INDIVIDUAL",
    "status": "ACTIVE",
    "risk_rating": "LOW",
    "kyc_completed": true,
    "relationship_manager_name": "Jane Smith",
    "active_companies_count": 3
  }
]
```

### Get Client Details
```
GET /api/offshore/clients/{id}/
```

**Response:**
```json
{
  "id": "uuid",
  "client_reference": "CLI-001",
  "client_type": "INDIVIDUAL",
  "client_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "country_of_residence": "United States",
  "kyc_completed": true,
  "kyc_completion_date": "2024-01-15",
  "kyc_review_date": "2025-01-15",
  "risk_rating": "LOW",
  "status": "ACTIVE",
  "onboarding_date": "2024-01-10",
  "relationship_manager": "uuid",
  "relationship_manager_name": "Jane Smith",
  "notes": "VIP client",
  "active_companies_count": 3,
  "kyc_status": "valid",
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2025-11-16T10:00:00Z"
}
```

**KYC Status Values:**
- `pending` - KYC not completed
- `valid` - KYC valid
- `review_due_soon` - Review due in next 30 days
- `review_overdue` - Review overdue

### Create Client
```
POST /api/offshore/clients/
```

**Request Body:**
```json
{
  "client_reference": "CLI-002",
  "client_type": "COMPANY",
  "client_name": "Acme Corp",
  "email": "contact@acme.com",
  "phone": "+1234567890",
  "address": "456 Business Ave",
  "country_of_residence": "United States",
  "kyc_completed": false,
  "risk_rating": "MEDIUM",
  "status": "PROSPECT",
  "relationship_manager": "uuid"
}
```

### Get Client Companies
```
GET /api/offshore/clients/{id}/companies/
```

Returns all active companies associated with this client.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Caribbean Trading Ltd",
    "jurisdiction": "BVI",
    "jurisdiction_display": "British Virgin Islands",
    "entity_type": "IBC",
    "entity_type_display": "International Business Company",
    "currency": "USD",
    "is_offshore": true,
    "days_until_renewal": 45,
    "annual_renewal_date": "2025-01-15",
    "is_active": true
  }
]
```

### Get Clients with KYC Review Due
```
GET /api/offshore/clients/kyc-review-due/
```

Returns clients with KYC review due in the next 30 days.

### Get Clients with Overdue KYC
```
GET /api/offshore/clients/kyc-overdue/
```

Returns active clients with overdue KYC review.

---

## 🔍 Common Response Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `501 Not Implemented` - Feature not yet implemented

---

## 📊 Pagination

List endpoints support pagination with the following parameters:

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10, max: 100)

**Response includes:**
```json
{
  "count": 100,
  "next": "http://api.example.com/api/offshore/annual-returns/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## 🔐 Authentication

All endpoints require authentication. Use one of:

1. **Session Authentication** (for browser-based clients)
2. **Token Authentication** (for API clients)

Include credentials in headers:
```
Authorization: Token your-token-here
```

Or use session cookies set by Django.

---

## 🚀 Next Steps

1. **Implement PDF Generation**: Replace stub implementations with actual PDF generation
2. **Add Email Notifications**: Send alerts for overdue items
3. **External API Integration**: Integrate with exchangerate-api.com for automatic rate updates
4. **Bulk Operations**: Add endpoints for bulk actions (mark multiple fees as paid, etc.)
5. **Analytics Endpoints**: Add summary/statistics endpoints for dashboard

---

**Last Updated:** November 16, 2025  
**API Version:** 2.0-offshore
