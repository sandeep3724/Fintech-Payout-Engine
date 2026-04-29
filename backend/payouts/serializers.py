from rest_framework import serializers
from .models import Payout


class PayoutCreateSerializer(serializers.Serializer):
    merchant_id = serializers.IntegerField()
    amount_paise = serializers.IntegerField(min_value=1)
    bank_account_id = serializers.IntegerField()


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = [
            "id",
            "merchant",
            "bank_account",
            "amount_paise",
            "status",
            "idempotency_key",
            "attempts",
            "failure_reason",
            "processing_started_at",
            "completed_at",
            "failed_at",
            "created_at",
        ]