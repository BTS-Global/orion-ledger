from django.contrib import admin
from .models import Company, UserProfile, ChartOfAccounts


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_id', 'owner', 'fiscal_year_start', 'created_at']
    list_filter = ['created_at', 'state']
    search_fields = ['name', 'tax_id', 'owner__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['users']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'active_company', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ['account_code', 'account_name', 'account_type', 'company', 'is_active']
    list_filter = ['account_type', 'is_active', 'company']
    search_fields = ['account_code', 'account_name']
    readonly_fields = ['created_at', 'updated_at']

