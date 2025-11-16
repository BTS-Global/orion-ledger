"""
Service for generating IRS tax forms from accounting data.
"""
from decimal import Decimal
from datetime import date
from typing import Dict, Any
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io

from companies.models import Company
from transactions.accounting_service import AccountingService
from .models import IRSForm


class IRSFormGenerator:
    """Generate IRS tax forms from accounting data."""
    
    def __init__(self, company: Company, tax_year: int):
        self.company = company
        self.tax_year = tax_year
        self.accounting_service = AccountingService(company)
    
    def generate_form_5472(self) -> IRSForm:
        """
        Generate Form 5472 - Information Return of a 25% Foreign-Owned U.S. Corporation.
        """
        # Get financial data for the tax year
        start_date = date(self.tax_year, 1, 1)
        end_date = date(self.tax_year, 12, 31)
        
        income_statement = self.accounting_service.get_income_statement(
            start_date=start_date,
            end_date=end_date
        )
        
        # Map accounting data to Form 5472 fields
        form_data = {
            'reporting_corp_name': self.company.name,
            'reporting_corp_ein': self.company.tax_id or '',
            'reporting_corp_address': self.company.address or '',
            'tax_year': self.tax_year,
            
            # Revenue data
            'sales_revenue': income_statement['revenues']['total'],
            'cost_of_goods_sold': 0,  # Would need specific account mapping
            'rents_received': 0,
            'royalties_received': 0,
            'interest_received': 0,
            
            # Note: Foreign shareholder info would need to be provided separately
            'foreign_shareholder_name': '',
            'foreign_shareholder_address': '',
            'foreign_shareholder_country': '',
        }
        
        # Create or update IRS Form
        irs_form, created = IRSForm.objects.update_or_create(
            company=self.company,
            form_type='5472',
            tax_year=self.tax_year,
            defaults={
                'form_data': form_data,
                'status': 'DRAFT'
            }
        )
        
        # Generate PDF
        pdf_content = self._generate_form_5472_pdf(form_data)
        irs_form.pdf_file.save(
            f'form_5472_{self.company.id}_{self.tax_year}.pdf',
            ContentFile(pdf_content),
            save=True
        )
        
        return irs_form
    
    def generate_form_1099_nec(self, recipient_data: Dict[str, Any]) -> IRSForm:
        """
        Generate Form 1099-NEC - Nonemployee Compensation.
        
        Args:
            recipient_data: Dict with recipient info (name, tin, address, amount)
        """
        form_data = {
            'payer_name': self.company.name,
            'payer_ein': self.company.tax_id or '',
            'payer_address': self.company.address or '',
            'tax_year': self.tax_year,
            
            'recipient_name': recipient_data.get('name', ''),
            'recipient_tin': recipient_data.get('tin', ''),
            'recipient_address': recipient_data.get('address', ''),
            
            'nonemployee_compensation': recipient_data.get('amount', 0),
            'direct_sales_indicator': recipient_data.get('direct_sales', False),
            'federal_tax_withheld': recipient_data.get('tax_withheld', 0),
        }
        
        # Create IRS Form (allow multiple 1099s per year)
        irs_form = IRSForm.objects.create(
            company=self.company,
            form_type='1099-NEC',
            tax_year=self.tax_year,
            form_data=form_data,
            status='DRAFT'
        )
        
        # Generate PDF
        pdf_content = self._generate_form_1099_nec_pdf(form_data)
        irs_form.pdf_file.save(
            f'form_1099_nec_{self.company.id}_{self.tax_year}_{irs_form.id}.pdf',
            ContentFile(pdf_content),
            save=True
        )
        
        return irs_form
    
    def generate_form_1120(self) -> IRSForm:
        """
        Generate Form 1120 - U.S. Corporation Income Tax Return.
        """
        # Get financial data for the tax year
        start_date = date(self.tax_year, 1, 1)
        end_date = date(self.tax_year, 12, 31)
        
        income_statement = self.accounting_service.get_income_statement(
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculate totals
        total_revenue = Decimal(str(income_statement['revenues']['total']))
        total_expenses = Decimal(str(income_statement['expenses']['total']))
        net_income = Decimal(str(income_statement['net_income']))
        
        # Map to Form 1120 fields
        form_data = {
            'company_name': self.company.name,
            'ein': self.company.tax_id or '',
            'address': self.company.address or '',
            'tax_year': self.tax_year,
            
            # Income
            'gross_receipts': float(total_revenue),
            'cost_of_goods_sold': 0,
            'gross_profit': float(total_revenue),
            'dividends': 0,
            'interest': 0,
            'gross_rents': 0,
            'gross_royalties': 0,
            'capital_gain_net_income': 0,
            'other_income': 0,
            'total_income': float(total_revenue),
            
            # Deductions (simplified - would need detailed account mapping)
            'compensation_of_officers': 0,
            'salaries_and_wages': 0,
            'repairs_and_maintenance': 0,
            'bad_debts': 0,
            'rents': 0,
            'taxes_and_licenses': 0,
            'interest_expense': 0,
            'charitable_contributions': 0,
            'depreciation': 0,
            'advertising': 0,
            'pension_plans': 0,
            'employee_benefit_programs': 0,
            'other_deductions': float(total_expenses),
            'total_deductions': float(total_expenses),
            
            # Tax computation
            'taxable_income': float(net_income),
            'total_tax': float(net_income * Decimal('0.21')),  # 21% corporate tax rate
        }
        
        # Create or update IRS Form
        irs_form, created = IRSForm.objects.update_or_create(
            company=self.company,
            form_type='1120',
            tax_year=self.tax_year,
            defaults={
                'form_data': form_data,
                'status': 'DRAFT'
            }
        )
        
        # Generate PDF
        pdf_content = self._generate_form_1120_pdf(form_data)
        irs_form.pdf_file.save(
            f'form_1120_{self.company.id}_{self.tax_year}.pdf',
            ContentFile(pdf_content),
            save=True
        )
        
        return irs_form
    
    def generate_form_1040(self, taxpayer_data: Dict[str, Any]) -> IRSForm:
        """
        Generate Form 1040 - U.S. Individual Income Tax Return.
        
        Args:
            taxpayer_data: Dict with taxpayer personal and income info
        """
        # Calculate standard deduction based on filing status
        standard_deductions = {
            'SINGLE': 14600,
            'MARRIED_JOINT': 29200,
            'MARRIED_SEPARATE': 14600,
            'HEAD_OF_HOUSEHOLD': 21900,
            'QUALIFYING_WIDOW': 29200,
        }
        
        filing_status = taxpayer_data.get('filing_status', 'SINGLE')
        total_income = Decimal(str(taxpayer_data.get('total_income', 0)))
        adjustments = Decimal(str(taxpayer_data.get('adjustments', 0)))
        
        agi = total_income - adjustments
        standard_deduction = Decimal(str(standard_deductions.get(filing_status, 14600)))
        taxable_income = max(agi - standard_deduction, Decimal('0'))
        
        # Simplified tax calculation (would need actual tax brackets)
        tax_rate = Decimal('0.22')  # Simplified
        total_tax = taxable_income * tax_rate
        
        form_data = {
            'taxpayer_name': taxpayer_data.get('name', ''),
            'taxpayer_ssn': taxpayer_data.get('ssn', ''),
            'spouse_name': taxpayer_data.get('spouse_name', ''),
            'spouse_ssn': taxpayer_data.get('spouse_ssn', ''),
            'address': taxpayer_data.get('address', ''),
            'filing_status': filing_status,
            'tax_year': self.tax_year,
            
            'wages': taxpayer_data.get('wages', 0),
            'interest': taxpayer_data.get('interest', 0),
            'dividends': taxpayer_data.get('dividends', 0),
            'business_income': taxpayer_data.get('business_income', 0),
            'capital_gains': taxpayer_data.get('capital_gains', 0),
            'other_income': taxpayer_data.get('other_income', 0),
            'total_income': float(total_income),
            
            'total_adjustments': float(adjustments),
            'adjusted_gross_income': float(agi),
            'standard_deduction': float(standard_deduction),
            'taxable_income': float(taxable_income),
            'total_tax': float(total_tax),
            
            'federal_tax_withheld': taxpayer_data.get('tax_withheld', 0),
            'estimated_tax_payments': taxpayer_data.get('estimated_payments', 0),
        }
        
        # Create IRS Form
        irs_form = IRSForm.objects.create(
            company=self.company,
            form_type='1040',
            tax_year=self.tax_year,
            form_data=form_data,
            status='DRAFT'
        )
        
        # Generate PDF
        pdf_content = self._generate_form_1040_pdf(form_data)
        irs_form.pdf_file.save(
            f'form_1040_{self.company.id}_{self.tax_year}_{irs_form.id}.pdf',
            ContentFile(pdf_content),
            save=True
        )
        
        return irs_form
    
    # PDF Generation Methods (simplified versions)
    
    def _generate_form_5472_pdf(self, data: Dict) -> bytes:
        """Generate PDF for Form 5472."""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1*inch, height - 1*inch, "Form 5472")
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, height - 1.3*inch, "Information Return of a 25% Foreign-Owned U.S. Corporation")
        
        # Tax Year
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, height - 1.8*inch, f"Tax Year: {data['tax_year']}")
        
        # Part I - Reporting Corporation
        y = height - 2.3*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "Part I - Reporting Corporation")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Name: {data['reporting_corp_name']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"EIN: {data['reporting_corp_ein']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Address: {data['reporting_corp_address']}")
        
        # Part IV - Monetary Transactions
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "Part IV - Monetary Transactions")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Sales Revenue: ${data['sales_revenue']:,.2f}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Cost of Goods Sold: ${data['cost_of_goods_sold']:,.2f}")
        
        # Footer
        p.setFont("Helvetica", 8)
        p.drawString(1*inch, 0.5*inch, "This is a simplified representation. Official IRS forms must be used for filing.")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer.read()
    
    def _generate_form_1099_nec_pdf(self, data: Dict) -> bytes:
        """Generate PDF for Form 1099-NEC."""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1*inch, height - 1*inch, "Form 1099-NEC")
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, height - 1.3*inch, "Nonemployee Compensation")
        
        # Tax Year
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, height - 1.8*inch, f"Tax Year: {data['tax_year']}")
        
        # Payer Information
        y = height - 2.3*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "PAYER'S Information")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Name: {data['payer_name']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"EIN: {data['payer_ein']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Address: {data['payer_address']}")
        
        # Recipient Information
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "RECIPIENT'S Information")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Name: {data['recipient_name']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"TIN: {data['recipient_tin']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Address: {data['recipient_address']}")
        
        # Box 1 - Nonemployee Compensation
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, y, f"Box 1 - Nonemployee Compensation: ${data['nonemployee_compensation']:,.2f}")
        
        # Footer
        p.setFont("Helvetica", 8)
        p.drawString(1*inch, 0.5*inch, "This is a simplified representation. Official IRS forms must be used for filing.")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer.read()
    
    def _generate_form_1120_pdf(self, data: Dict) -> bytes:
        """Generate PDF for Form 1120."""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1*inch, height - 1*inch, "Form 1120")
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, height - 1.3*inch, "U.S. Corporation Income Tax Return")
        
        # Tax Year
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, height - 1.8*inch, f"Tax Year: {data['tax_year']}")
        
        # Company Information
        y = height - 2.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Company: {data['company_name']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"EIN: {data['ein']}")
        
        # Income Section
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "INCOME")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Gross Receipts: ${data['gross_receipts']:,.2f}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Total Income: ${data['total_income']:,.2f}")
        
        # Deductions Section
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "DEDUCTIONS")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Total Deductions: ${data['total_deductions']:,.2f}")
        
        # Tax Computation
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "TAX COMPUTATION")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Taxable Income: ${data['taxable_income']:,.2f}")
        y -= 0.2*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, f"Total Tax: ${data['total_tax']:,.2f}")
        
        # Footer
        p.setFont("Helvetica", 8)
        p.drawString(1*inch, 0.5*inch, "This is a simplified representation. Official IRS forms must be used for filing.")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer.read()
    
    def _generate_form_1040_pdf(self, data: Dict) -> bytes:
        """Generate PDF for Form 1040."""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1*inch, height - 1*inch, "Form 1040")
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, height - 1.3*inch, "U.S. Individual Income Tax Return")
        
        # Tax Year
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, height - 1.8*inch, f"Tax Year: {data['tax_year']}")
        
        # Personal Information
        y = height - 2.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Name: {data['taxpayer_name']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"SSN: {data['taxpayer_ssn']}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Filing Status: {data['filing_status']}")
        
        # Income
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "INCOME")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Total Income: ${data['total_income']:,.2f}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Adjusted Gross Income: ${data['adjusted_gross_income']:,.2f}")
        
        # Deductions and Tax
        y -= 0.5*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, "DEDUCTIONS AND TAX")
        
        y -= 0.3*inch
        p.setFont("Helvetica", 10)
        p.drawString(1*inch, y, f"Standard Deduction: ${data['standard_deduction']:,.2f}")
        y -= 0.2*inch
        p.drawString(1*inch, y, f"Taxable Income: ${data['taxable_income']:,.2f}")
        y -= 0.2*inch
        p.setFont("Helvetica-Bold", 11)
        p.drawString(1*inch, y, f"Total Tax: ${data['total_tax']:,.2f}")
        
        # Footer
        p.setFont("Helvetica", 8)
        p.drawString(1*inch, 0.5*inch, "This is a simplified representation. Official IRS forms must be used for filing.")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer.read()

