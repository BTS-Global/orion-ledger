from rest_framework import serializers
from .models import Transaction, JournalEntry, JournalEntryLine


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""
    
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    validated_by_email = serializers.EmailField(source='validated_by.email', read_only=True)
    document_name = serializers.CharField(source='document.file_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'company', 'date', 'description', 'amount', 
            'account', 'account_name', 'account_code',
            'document', 'document_name',
            'is_validated', 'validated_by', 'validated_by_email', 'validated_at',
            'suggested_category', 'confidence_score',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'validated_by', 'validated_at', 
            'suggested_category', 'confidence_score',
            'created_at', 'updated_at'
        ]


class TransactionValidateSerializer(serializers.Serializer):
    """Serializer for validating a transaction."""
    
    account = serializers.UUIDField(required=True)
    
    def validate_account(self, value):
        """Ensure account exists and belongs to the same company."""
        from companies.models import ChartOfAccounts
        
        try:
            account = ChartOfAccounts.objects.get(id=value)
            if not account.is_active:
                raise serializers.ValidationError("Selected account is not active")
            return value
        except ChartOfAccounts.DoesNotExist:
            raise serializers.ValidationError("Account not found")


class JournalEntryLineSerializer(serializers.ModelSerializer):
    """Serializer for Journal Entry Lines."""
    
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    
    class Meta:
        model = JournalEntryLine
        fields = [
            'id', 'account', 'account_name', 'account_code',
            'debit', 'credit', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JournalEntrySerializer(serializers.ModelSerializer):
    """Serializer for Journal Entry."""
    
    lines = JournalEntryLineSerializer(many=True, read_only=True)
    is_balanced = serializers.BooleanField(read_only=True)
    total_debit = serializers.SerializerMethodField()
    total_credit = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'company', 'date', 'description', 'reference',
            'transaction', 'lines', 'is_balanced', 
            'total_debit', 'total_credit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_debit(self, obj):
        return sum(line.debit for line in obj.lines.all())
    
    def get_total_credit(self, obj):
        return sum(line.credit for line in obj.lines.all())

