from django.contrib import admin
from .models import AuditLog
from .feedback_service import FeedbackEntry, PredictionMetrics


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__email', 'action', 'details']
    readonly_fields = ['id', 'timestamp']
    
    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit logs
        return False


@admin.register(FeedbackEntry)
class FeedbackEntryAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'feedback_type', 'user', 'predicted_confidence', 'timestamp']
    list_filter = ['feedback_type', 'timestamp']
    search_fields = ['transaction__description', 'user__email', 'correction_reason']
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'


@admin.register(PredictionMetrics)
class PredictionMetricsAdmin(admin.ModelAdmin):
    list_display = ['company', 'date', 'total_predictions', 'correct_predictions', 'accuracy_display', 'avg_confidence']
    list_filter = ['date', 'company']
    search_fields = ['company__name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'accuracy_display']
    date_hierarchy = 'date'
    
    def accuracy_display(self, obj):
        return f"{obj.accuracy:.1f}%"
    accuracy_display.short_description = 'Accuracy'

