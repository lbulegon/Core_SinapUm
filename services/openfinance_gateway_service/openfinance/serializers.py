"""
Serializers Open Finance.
"""
from rest_framework import serializers
from .models import OF_Consent, OF_Account, OF_Transaction


class ConsentCreateSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=255)
    origin_system = serializers.ChoiceField(choices=['paypi', 'motopro', 'vitrinezap', 'other'])
    scope = serializers.JSONField(default=dict)


class ConsentResponseSerializer(serializers.Serializer):
    consent_id = serializers.UUIDField()
    redirect_url = serializers.URLField(allow_blank=True)
    expires_at = serializers.DateTimeField(allow_null=True)


class SyncRequestSerializer(serializers.Serializer):
    consent_id = serializers.UUIDField()
    from_date = serializers.DateTimeField(required=False, allow_null=True)
    to_date = serializers.DateTimeField(required=False, allow_null=True)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OF_Account
        fields = [
            'id',
            'external_account_id',
            'type',
            'currency',
            'masked_number',
            'owner_name',
            'owner_doc',
            'created_at',
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OF_Transaction
        fields = [
            'id',
            'external_tx_id',
            'date',
            'amount',
            'direction',
            'description',
            'created_at',
        ]
