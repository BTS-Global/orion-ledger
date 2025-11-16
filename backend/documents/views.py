from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from companies.models import Company


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Document CRUD operations."""
    
    permission_classes = []  # Temporarily allow any for testing
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Return documents for companies accessible to the current user."""
        if self.request.user.is_authenticated:
            user = self.request.user
            accessible_companies = Company.objects.filter(owner=user) | Company.objects.filter(users=user)
            queryset = Document.objects.filter(company__in=accessible_companies)
        else:
            queryset = Document.objects.all()
        
        # Filter by company if provided
        company_id = self.request.query_params.get('company', None)
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Handle document upload."""
        serializer = DocumentUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        file = serializer.validated_data['file']
        company_id = serializer.validated_data['company']
        
        # Verify company exists (authentication disabled temporarily)
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Save file
        import os
        from django.conf import settings
        
        # Create media directory if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'documents', str(company_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with unique name
        import uuid
        file_ext = file.name.split('.')[-1].lower()
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(upload_dir, file_name)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Create document record
        document = Document.objects.create(
            company=company,
            file_path=file_path,
            file_name=file.name,
            file_type=file_ext.upper(),
            file_size=file.size,
            uploaded_by=request.user if request.user.is_authenticated else None,
            status='UPLOADED'
        )
        
        # Trigger async processing task
        from documents.tasks import process_document
        process_document.delay(str(document.id))
        
        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def status_check(self, request, pk=None):
        """Check the processing status of a document."""
        document = self.get_object()
        return Response({
            'id': str(document.id),
            'status': document.status,
            'file_name': document.file_name,
            'processing_result': document.processing_result,
            'error_message': document.error_message
        })
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a failed or completed document."""
        document = self.get_object()
        
        # Check if can retry
        if not document.can_retry():
            return Response(
                {'error': 'Maximum retry attempts reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset status
        document.status = 'UPLOADED'
        document.error_message = None
        document.error_log = None
        document.processing_progress = {}
        document.save()
        
        # Trigger async processing task
        from documents.tasks import process_document
        process_document.delay(str(document.id))
        
        return Response({
            'message': 'Document reprocessing started',
            'document_id': str(document.id)
        })
    
    @action(detail=True, methods=['get'])
    def extracted_data(self, request, pk=None):
        """Get extracted transactions for review."""
        document = self.get_object()
        
        if document.status != 'READY_FOR_REVIEW':
            return Response(
                {'error': 'Document is not ready for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'document_id': str(document.id),
            'file_name': document.file_name,
            'status': document.status,
            'extracted_data': document.extracted_data,
            'transactions': document.extracted_data.get('transactions', []),
            'validation': document.extracted_data.get('validation', {})
        })
    
    @action(detail=True, methods=['post'])
    def confirm_transactions(self, request, pk=None):
        """Confirm and create transactions from extracted data."""
        document = self.get_object()
        
        if document.status != 'READY_FOR_REVIEW':
            return Response(
                {'error': 'Document is not ready for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get transactions to create (can be edited by user)
        transactions_data = request.data.get('transactions', [])
        
        if not transactions_data:
            # Use extracted data if no modifications
            transactions_data = document.extracted_data.get('transactions', [])
        
        # Create transactions
        from documents.tasks import create_transactions_from_result
        created_count = create_transactions_from_result(
            document,
            {'transactions': transactions_data}
        )
        
        # Update document status
        document.status = 'COMPLETED'
        document.save()
        
        return Response({
            'message': f'{created_count} transactions created successfully',
            'transactions_created': created_count
        })
    
    @action(detail=True, methods=['post'])
    def reject_transactions(self, request, pk=None):
        """Reject extracted transactions."""
        document = self.get_object()
        
        # Mark as completed without creating transactions
        document.status = 'COMPLETED'
        document.extracted_data = {}
        document.save()
        
        return Response({
            'message': 'Transactions rejected'
        })
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get processing progress."""
        document = self.get_object()
        
        return Response({
            'document_id': str(document.id),
            'status': document.status,
            'processing_progress': document.processing_progress,
            'processing_attempts': document.processing_attempts,
            'can_retry': document.can_retry()
        })

