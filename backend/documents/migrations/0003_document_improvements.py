# Generated manually for Phase 1 improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_alter_document_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='processing_progress',
            field=models.JSONField(blank=True, default=dict, help_text='Current processing progress'),
        ),
        migrations.AddField(
            model_name='document',
            name='error_log',
            field=models.TextField(blank=True, help_text='Detailed error log', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='processing_attempts',
            field=models.IntegerField(default=0, help_text='Number of processing attempts'),
        ),
        migrations.AddField(
            model_name='document',
            name='extracted_data',
            field=models.JSONField(blank=True, default=dict, help_text='Extracted data pending review'),
        ),
        migrations.AlterField(
            model_name='document',
            name='status',
            field=models.CharField(
                choices=[
                    ('UPLOADED', 'Uploaded'),
                    ('PROCESSING', 'Processing'),
                    ('COMPLETED', 'Completed'),
                    ('FAILED', 'Failed'),
                    ('READY_FOR_REVIEW', 'Ready for Review'),
                ],
                default='UPLOADED',
                max_length=20
            ),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['company', 'status'], name='documents_d_company_b82d07_idx'),
        ),
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['upload_date'], name='documents_d_upload__24c17c_idx'),
        ),
    ]
