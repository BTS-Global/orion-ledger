from rest_framework import serializers
from .models import (
    AnnualReturn,
    EconomicSubstanceReport,
    JurisdictionFee,
    ExchangeRate,
    CorporateServiceClient
)
from companies.models import Company


class AnnualReturnSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_jurisdiction = serializers.CharField(source='company.jurisdiction', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AnnualReturn
        fields = [
            'id', 'company', 'company_name', 'company_jurisdiction',
            'filing_year', 'due_date', 'filed_date', 'status',
            'reference_number', 'total_assets', 'total_liabilities',
            'total_equity', 'net_income', 'pdf_file',
            'supporting_documents', 'notes', 'created_by',
            'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnnualReturnListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views."""
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_jurisdiction = serializers.CharField(source='company.jurisdiction', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AnnualReturn
        fields = [
            'id', 'company', 'company_name', 'company_jurisdiction',
            'filing_year', 'due_date', 'filed_date', 'status',
            'is_overdue'
        ]


class EconomicSubstanceReportSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_jurisdiction = serializers.CharField(source='company.jurisdiction', read_only=True)
    business_activity_display = serializers.CharField(source='get_business_activity_display', read_only=True)
    
    class Meta:
        model = EconomicSubstanceReport
        fields = [
            'id', 'company', 'company_name', 'company_jurisdiction',
            'reporting_year', 'submission_deadline', 'submission_date',
            'business_activity', 'business_activity_display',
            'activity_description', 'has_adequate_employees',
            'num_employees', 'has_adequate_premises', 'premises_address',
            'has_adequate_expenditure', 'annual_expenditure',
            'conducts_core_activities', 'core_activities_description',
            'is_pure_equity_holding', 'meets_reduced_substance',
            'meets_substance_requirements', 'status', 'reference_number',
            'pdf_file', 'notes', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JurisdictionFeeSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_jurisdiction = serializers.CharField(source='company.jurisdiction', read_only=True)
    fee_type_display = serializers.CharField(source='get_fee_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = JurisdictionFee
        fields = [
            'id', 'company', 'company_name', 'company_jurisdiction',
            'fee_type', 'fee_type_display', 'description', 'amount',
            'currency', 'due_date', 'paid_date', 'status',
            'status_display', 'payment_reference', 'notes',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = [
            'id', 'from_currency', 'to_currency', 'rate',
            'date', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CurrencyConversionSerializer(serializers.Serializer):
    """Serializer for currency conversion requests."""
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    date = serializers.DateField()


class CurrencyConversionResponseSerializer(serializers.Serializer):
    """Serializer for currency conversion responses."""
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    from_currency = serializers.CharField(max_length=3)
    to_currency = serializers.CharField(max_length=3)
    converted_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    rate = serializers.DecimalField(max_digits=18, decimal_places=6)
    date = serializers.DateField()


class CorporateServiceClientSerializer(serializers.ModelSerializer):
    relationship_manager_name = serializers.CharField(
        source='relationship_manager.get_full_name',
        read_only=True,
        allow_null=True
    )
    active_companies_count = serializers.SerializerMethodField()
    kyc_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CorporateServiceClient
        fields = [
            'id', 'client_reference', 'client_type', 'client_name',
            'email', 'phone', 'address', 'country_of_residence',
            'kyc_completed', 'kyc_completion_date', 'kyc_review_date',
            'risk_rating', 'status', 'onboarding_date',
            'relationship_manager', 'relationship_manager_name',
            'notes', 'active_companies_count', 'kyc_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_active_companies_count(self, obj):
        return obj.get_active_companies().count()
    
    def get_kyc_status(self, obj):
        """Get KYC status with review date check."""
        if not obj.kyc_completed:
            return 'pending'
        
        if obj.kyc_review_date:
            from django.utils import timezone
            if timezone.now().date() > obj.kyc_review_date:
                return 'review_overdue'
            elif (obj.kyc_review_date - timezone.now().date()).days <= 30:
                return 'review_due_soon'
        
        return 'valid'


class CorporateServiceClientListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views."""
    relationship_manager_name = serializers.CharField(
        source='relationship_manager.get_full_name',
        read_only=True,
        allow_null=True
    )
    active_companies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CorporateServiceClient
        fields = [
            'id', 'client_reference', 'client_name', 'client_type',
            'status', 'risk_rating', 'kyc_completed',
            'relationship_manager_name', 'active_companies_count'
        ]
    
    def get_active_companies_count(self, obj):
        return obj.get_active_companies().count()


class CompanyOffshoreSerializer(serializers.ModelSerializer):
    """Extended Company serializer with offshore-specific fields."""
    jurisdiction_display = serializers.CharField(source='get_jurisdiction_display', read_only=True)
    entity_type_display = serializers.CharField(source='get_entity_type_display', read_only=True)
    corporate_client_name = serializers.CharField(source='corporate_client.client_name', read_only=True, allow_null=True)
    is_offshore = serializers.BooleanField(read_only=True)
    days_until_renewal = serializers.IntegerField(read_only=True, allow_null=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'jurisdiction', 'jurisdiction_display',
            'entity_type', 'entity_type_display', 'tax_id',
            'registration_number', 'incorporation_date',
            'fiscal_year_start', 'address', 'city', 'state',
            'zip_code', 'country', 'phone', 'email',
            'registered_agent_name', 'registered_agent_address',
            'client_reference', 'annual_renewal_date', 'annual_fee',
            'currency', 'is_active', 'notes', 'corporate_client',
            'corporate_client_name', 'is_offshore', 'days_until_renewal',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
