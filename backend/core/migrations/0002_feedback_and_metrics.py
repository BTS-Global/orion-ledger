# Generated migration for Feedback and Metrics models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('companies', '0001_initial'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        # Create FeedbackEntry model
        migrations.CreateModel(
            name='FeedbackEntry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('predicted_confidence', models.FloatField(default=0.0)),
                ('feedback_type', models.CharField(choices=[('CORRECTION', 'Correction'), ('CONFIRMATION', 'Confirmation'), ('REJECTION', 'Rejection')], max_length=20)),
                ('correction_reason', models.TextField(blank=True, help_text='Why was the prediction wrong?')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('corrected_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='corrected_to', to='companies.chartofaccounts')),
                ('predicted_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='predicted_for', to='companies.chartofaccounts')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='transactions.transaction')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        
        # Create PredictionMetrics model
        migrations.CreateModel(
            name='PredictionMetrics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('total_predictions', models.IntegerField(default=0)),
                ('correct_predictions', models.IntegerField(default=0)),
                ('incorrect_predictions', models.IntegerField(default=0)),
                ('avg_confidence', models.FloatField(default=0.0)),
                ('high_confidence_correct', models.IntegerField(default=0, help_text='Correct with >0.8 confidence')),
                ('high_confidence_incorrect', models.IntegerField(default=0, help_text='Incorrect with >0.8 confidence')),
                ('low_confidence_correct', models.IntegerField(default=0, help_text='Correct with <0.6 confidence')),
                ('low_confidence_incorrect', models.IntegerField(default=0, help_text='Incorrect with <0.6 confidence')),
                ('avg_processing_time', models.FloatField(default=0.0, help_text='Average time in seconds')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='metrics', to='companies.company')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        
        # Add indexes for FeedbackEntry
        migrations.AddIndex(
            model_name='feedbackentry',
            index=models.Index(fields=['transaction', 'feedback_type'], name='core_feedback_transaction_idx'),
        ),
        migrations.AddIndex(
            model_name='feedbackentry',
            index=models.Index(fields=['timestamp'], name='core_feedback_timestamp_idx'),
        ),
        
        # Add indexes and unique constraint for PredictionMetrics
        migrations.AddIndex(
            model_name='predictionmetrics',
            index=models.Index(fields=['company', 'date'], name='core_metrics_company_date_idx'),
        ),
        migrations.AddConstraint(
            model_name='predictionmetrics',
            constraint=models.UniqueConstraint(fields=['company', 'date'], name='core_unique_company_date'),
        ),
    ]
