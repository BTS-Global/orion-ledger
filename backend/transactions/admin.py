from django.contrib import admin
from .models import Transaction, JournalEntry, JournalEntryLine


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'description_short', 'amount', 'account', 'is_validated', 'company']
    list_filter = ['is_validated', 'date', 'company']
    search_fields = ['description', 'company__name']
    readonly_fields = ['id', 'validated_at', 'created_at', 'updated_at']
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'description_short', 'company', 'is_balanced', 'created_at']
    list_filter = ['date', 'company']
    search_fields = ['description', 'reference']
    readonly_fields = ['id', 'is_balanced', 'created_at', 'updated_at']
    inlines = [JournalEntryLineInline]
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

