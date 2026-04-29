from django.db.models import Sum, Case, When, F, BigIntegerField, Value
from django.db.models.functions import Coalesce
from .models import LedgerEntry


def get_available_balance_paise(merchant):
    result = LedgerEntry.objects.filter(merchant=merchant).aggregate(
        balance=Coalesce(
            Sum(
                Case(
                    When(entry_type=LedgerEntry.CREDIT, then=F("amount_paise")),
                    When(entry_type=LedgerEntry.DEBIT, then=-F("amount_paise")),
                    default=Value(0),
                    output_field=BigIntegerField(),
                )
            ),
            Value(0),
            output_field=BigIntegerField(),
        )
    )

    return result["balance"]