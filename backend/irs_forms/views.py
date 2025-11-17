"""
Views for IRS tax forms.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse

from companies.models import Company
from .models import IRSForm
from .serializers import IRSFormSerializer
from .form_generator import IRSFormGenerator


class IRSFormViewSet(viewsets.ModelViewSet):
    """ViewSet for IRS tax forms."""
    
    serializer_class = IRSFormSerializer
    permission_classes = []  # Temporarily allow any for testing
    
    def get_queryset(self):
        """Filter forms by user's companies."""
        # Get companies the user has access to
        user_companies = Company.objects.all()  # Simplified - would filter by user
        
        # Optimize queries to prevent N+1 problem
        return IRSForm.objects.filter(
            company__in=user_companies
        ).select_related(
            'company',
            'created_by'
        )
    
    @action(detail=False, methods=['post'])
    def generate_5472(self, request):
        """Generate Form 5472."""
        company_id = request.data.get('company_id')
        tax_year = request.data.get('tax_year')
        
        if not company_id or not tax_year:
            return Response(
                {'error': 'company_id and tax_year are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
            generator = IRSFormGenerator(company, int(tax_year))
            irs_form = generator.generate_form_5472()
            
            serializer = self.get_serializer(irs_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_1099_nec(self, request):
        """Generate Form 1099-NEC."""
        company_id = request.data.get('company_id')
        tax_year = request.data.get('tax_year')
        recipient_data = request.data.get('recipient_data', {})
        
        if not company_id or not tax_year:
            return Response(
                {'error': 'company_id and tax_year are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
            generator = IRSFormGenerator(company, int(tax_year))
            irs_form = generator.generate_form_1099_nec(recipient_data)
            
            serializer = self.get_serializer(irs_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_1120(self, request):
        """Generate Form 1120."""
        company_id = request.data.get('company_id')
        tax_year = request.data.get('tax_year')
        
        if not company_id or not tax_year:
            return Response(
                {'error': 'company_id and tax_year are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
            generator = IRSFormGenerator(company, int(tax_year))
            irs_form = generator.generate_form_1120()
            
            serializer = self.get_serializer(irs_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_1040(self, request):
        """Generate Form 1040."""
        company_id = request.data.get('company_id')
        tax_year = request.data.get('tax_year')
        taxpayer_data = request.data.get('taxpayer_data', {})
        
        if not company_id or not tax_year:
            return Response(
                {'error': 'company_id and tax_year are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
            generator = IRSFormGenerator(company, int(tax_year))
            irs_form = generator.generate_form_1040(taxpayer_data)
            
            serializer = self.get_serializer(irs_form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Company.DoesNotExist:
            return Response(
                {'error': 'Company not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download PDF or CSV of the form."""
        irs_form = self.get_object()
        export_format = request.query_params.get('export_format', 'pdf').lower()
        
        if export_format == 'csv':
            return self._export_form_csv(irs_form)
        else:
            # PDF download
            if not irs_form.pdf_file:
                return Response(
                    {'error': 'PDF not generated yet'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return FileResponse(
                irs_form.pdf_file.open('rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=f'{irs_form.form_type}_{irs_form.tax_year}.pdf'
            )
    
    @action(detail=True, methods=['post'])
    def mark_as_filed(self, request, pk=None):
        """Mark form as filed."""
        irs_form = self.get_object()
        irs_form.status = 'FILED'
        irs_form.save()
        
        serializer = self.get_serializer(irs_form)
        return Response(serializer.data)



    def _export_form_csv(self, irs_form):
        """Export IRS form data to CSV."""
        import csv
        from io import StringIO
        from django.http import HttpResponse
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([f'IRS Form {irs_form.form_type}'])
        writer.writerow([f'Tax Year: {irs_form.tax_year}'])
        writer.writerow([f'Status: {irs_form.status}'])
        writer.writerow([f'Generated: {irs_form.created_at.strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])
        
        # Form data
        writer.writerow(['Field', 'Value'])
        writer.writerow([])
        
        form_data = irs_form.form_data
        
        # Export all form data fields
        for key, value in form_data.items():
            # Format field name (convert snake_case to Title Case)
            field_name = key.replace('_', ' ').title()
            
            # Format value
            if isinstance(value, (int, float)):
                if 'amount' in key.lower() or 'revenue' in key.lower() or 'expense' in key.lower() or 'income' in key.lower() or 'tax' in key.lower():
                    formatted_value = f'${value:,.2f}'
                else:
                    formatted_value = str(value)
            else:
                formatted_value = str(value)
            
            writer.writerow([field_name, formatted_value])
        
        # Footer
        writer.writerow([])
        writer.writerow(['Note', 'This is a simplified representation. Official IRS forms must be used for filing.'])
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="form_{irs_form.form_type}_{irs_form.tax_year}.csv"'
        
        return response

