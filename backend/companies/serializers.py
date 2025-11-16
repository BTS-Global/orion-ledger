from rest_framework import serializers
from .models import Company, UserProfile, ChartOfAccounts
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    user = UserSerializer(read_only=True)
    active_company_name = serializers.CharField(source='active_company.name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'active_company', 'active_company_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChartOfAccountsSerializer(serializers.ModelSerializer):
    """Serializer for Chart of Accounts."""
    
    parent_account_name = serializers.CharField(source='parent_account.account_name', read_only=True)
    
    class Meta:
        model = ChartOfAccounts
        fields = [
            'id', 'company', 'account_code', 'account_name', 'account_type', 
            'description', 'parent_account', 'parent_account_name', 
            'irs_box_mapping', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for Company model."""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    accounts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'tax_id', 'fiscal_year_start', 'address', 
            'city', 'state', 'zip_code', 'phone', 'email',
            'owner', 'owner_email', 'users', 'accounts_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_accounts_count(self, obj):
        return obj.accounts.filter(is_active=True).count()


class CompanyDetailSerializer(CompanySerializer):
    """Detailed serializer for Company with nested accounts."""
    
    accounts = ChartOfAccountsSerializer(many=True, read_only=True)
    
    class Meta(CompanySerializer.Meta):
        fields = CompanySerializer.Meta.fields + ['accounts']

