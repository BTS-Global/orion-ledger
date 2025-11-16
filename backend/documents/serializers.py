from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""
    
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'company', 'company_name', 'file_path', 'file_name', 
            'file_type', 'file_size', 'status', 'processing_result', 
            'error_message', 'uploaded_by', 'uploaded_by_email', 
            'upload_date', 'processed_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'processing_result', 'error_message', 
            'uploaded_by', 'upload_date', 'processed_date', 
            'created_at', 'updated_at'
        ]


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload."""
    
    file = serializers.FileField()
    company = serializers.UUIDField()
    
    def validate_file(self, value):
        """Validate file type and size."""
        # Check file extension
        allowed_extensions = ['pdf', 'csv', 'jpg', 'jpeg', 'png']
        ext = value.name.split('.')[-1].lower()
        
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size of 10MB. Your file is {value.size / (1024*1024):.2f}MB"
            )
        
        return value

