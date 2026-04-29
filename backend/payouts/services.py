from django.db import transaction
from django.utils import timezone

from ledger.models import LedgerEntry
from .models import Payout


ALLOWED_TRANSITIONS = {
    Payout.PENDING: [Payout.PROCESSING],
    Payout.PROCESSING: [Payout.COMPLETED, Payout.FAILED],
    Payout.COMPLETED: [],
    Payout.FAILED: [],
}


def transition_payout_status(payout, new_status, failure_reason=None):
    old_status = payout.status

    if new_status not in ALLOWED_TRANSITIONS[old_status]:
        raise ValueError(f"Invalid transition: {old_status} -> {new_status}")

    with transaction.atomic():
        payout = Payout.objects.select_for_update().get(id=payout.id)

        old_status = payout.status

        if new_status not in ALLOWED_TRANSITIONS[old_status]:
            raise ValueError(f"Invalid transition: {old_status} -> {new_status}")

        payout.status = new_status

        if new_status == Payout.PROCESSING:
            payout.processing_started_at = timezone.now()

        elif new_status == Payout.COMPLETED:
            payout.completed_at = timezone.now()

        elif new_status == Payout.FAILED:
            payout.failed_at = timezone.now()
            payout.failure_reason = failure_reason or "Payout failed"

            LedgerEntry.objects.create(
                merchant=payout.merchant,
                entry_type=LedgerEntry.CREDIT,
                amount_paise=payout.amount_paise,
                description=f"Refund for failed payout #{payout.id}",
                reference_id=f"refund:{payout.id}",
            )

        payout.save()

        return payout