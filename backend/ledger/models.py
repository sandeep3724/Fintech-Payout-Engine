from django.db import models
from merchants.models import Merchant


class LedgerEntry(models.Model):
    CREDIT = "credit"
    DEBIT = "debit"

    ENTRY_TYPES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
    ]

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="ledger_entries"
    )
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    amount_paise = models.BigIntegerField()
    description = models.CharField(max_length=255)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)