# Generated migration for RAG features - Transaction model updates

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        # Add new fields to Transaction model for RAG support
        migrations.AddField(
            model_name='transaction',
            name='vendor',
            field=models.CharField(blank=True, help_text='Vendor/merchant name', max_length=255),
        ),
        migrations.AddField(
            model_name='transaction',
            name='category',
            field=models.CharField(blank=True, help_text='Transaction category', max_length=100),
        ),
        migrations.AddField(
            model_name='transaction',
            name='embedding',
            field=models.JSONField(blank=True, help_text='Vector embedding for RAG', null=True),
        ),
    ]
