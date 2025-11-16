"""
Serializers for IRS forms.
"""
from rest_framework import serializers
from .models import IRSForm


class IRSFormSerializer(serializers.ModelSerializer):
    """Serializer for IRS forms."""
    
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = IRSForm
        fields = [
            'id', 'company', 'form_type', 'tax_year', 'status',
            'form_data', 'pdf_file', 'pdf_url',
            'created_at', 'updated_at', 'filed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'pdf_file', 'pdf_url']
    
    def get_pdf_url(self, obj):
        """Get URL for PDF file."""
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return None

