from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'company', 'file_type', 'status', 'uploaded_by', 'upload_date']
    list_filter = ['status', 'file_type', 'upload_date']
    search_fields = ['file_name', 'company__name', 'uploaded_by__email']
    readonly_fields = ['id', 'upload_date', 'processed_date', 'created_at', 'updated_at']

