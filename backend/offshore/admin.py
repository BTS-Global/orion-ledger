from django.contrib import admin
from .models import (
    AnnualReturn,
    EconomicSubstanceReport,
    JurisdictionFee,
    ExchangeRate,
    CorporateServiceClient
)


@admin.register(AnnualReturn)
class AnnualReturnAdmin(admin.ModelAdmin):
    list_display = ['company', 'filing_year', 'due_date', 'status', 'filed_date']
    list_filter = ['status', 'filing_year']
    search_fields = ['company__name', 'reference_number']
    date_hierarchy = 'due_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company',)
        }),
        ('Filing Details', {
            'fields': ('filing_year', 'due_date', 'filed_date', 'status', 'reference_number')
        }),
        ('Financial Summary', {
            'fields': ('total_assets', 'total_liabilities', 'total_equity', 'net_income')
        }),
        ('Documents', {
            'fields': ('pdf_file', 'supporting_documents')
        }),
        ('Metadata', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EconomicSubstanceReport)
class EconomicSubstanceReportAdmin(admin.ModelAdmin):
    list_display = ['company', 'reporting_year', 'business_activity', 'meets_substance_requirements', 'status']
    list_filter = ['status', 'business_activity', 'meets_substance_requirements', 'reporting_year']
    search_fields = ['company__name', 'reference_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company',)
        }),
        ('Reporting Period', {
            'fields': ('reporting_year', 'submission_deadline', 'submission_date', 'status', 'reference_number')
        }),
        ('Business Activity', {
            'fields': ('business_activity', 'activity_description')
        }),
        ('Substance Requirements', {
            'fields': (
                'has_adequate_employees', 'num_employees',
                'has_adequate_premises', 'premises_address',
                'has_adequate_expenditure', 'annual_expenditure',
                'conducts_core_activities', 'core_activities_description'
            )
        }),
        ('Holding Company', {
            'fields': ('is_pure_equity_holding', 'meets_reduced_substance'),
            'classes': ('collapse',)
        }),
        ('Assessment', {
            'fields': ('meets_substance_requirements',)
        }),
        ('Documents', {
            'fields': ('pdf_file',)
        }),
        ('Metadata', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JurisdictionFee)
class JurisdictionFeeAdmin(admin.ModelAdmin):
    list_display = ['company', 'fee_type', 'amount', 'currency', 'due_date', 'status']
    list_filter = ['status', 'fee_type', 'currency']
    search_fields = ['company__name', 'description', 'payment_reference']
    date_hierarchy = 'due_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company',)
        }),
        ('Fee Details', {
            'fields': ('fee_type', 'description', 'amount', 'currency')
        }),
        ('Payment Tracking', {
            'fields': ('due_date', 'paid_date', 'status', 'payment_reference')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['from_currency', 'to_currency', 'rate', 'date', 'source']
    list_filter = ['from_currency', 'to_currency', 'source']
    search_fields = ['from_currency', 'to_currency']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Exchange Rate', {
            'fields': ('from_currency', 'to_currency', 'rate', 'date', 'source')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CorporateServiceClient)
class CorporateServiceClientAdmin(admin.ModelAdmin):
    list_display = ['client_reference', 'client_name', 'client_type', 'status', 'risk_rating', 'relationship_manager']
    list_filter = ['status', 'client_type', 'risk_rating', 'kyc_completed']
    search_fields = ['client_reference', 'client_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_reference', 'client_type', 'client_name')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'address', 'country_of_residence')
        }),
        ('KYC/Due Diligence', {
            'fields': ('kyc_completed', 'kyc_completion_date', 'kyc_review_date', 'risk_rating')
        }),
        ('Status', {
            'fields': ('status', 'onboarding_date', 'relationship_manager')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
