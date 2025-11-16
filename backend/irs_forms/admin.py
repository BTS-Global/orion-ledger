from django.contrib import admin
from .models import IRSForm


@admin.register(IRSForm)
class IRSFormAdmin(admin.ModelAdmin):
    list_display = ['form_type', 'company', 'tax_year', 'status', 'created_at']
    list_filter = ['form_type', 'status', 'tax_year']
    search_fields = ['company__company_name']
    readonly_fields = ['created_at', 'updated_at']
