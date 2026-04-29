import random
import time

from celery import shared_task

from .models import Payout
from .services import transition_payout_status


@shared_task
def process_payout(payout_id):
    try:
        payout = Payout.objects.get(id=payout_id)

        if payout.status != Payout.PENDING:
            return

        payout = transition_payout_status(payout, Payout.PROCESSING)

        time.sleep(2)

        outcome = random.choices(
            ["success", "fail", "hang"],
            weights=[70, 20, 10],
        )[0]

        if outcome == "success":
            transition_payout_status(payout, Payout.COMPLETED)

        elif outcome == "fail":
            transition_payout_status(
                payout,
                Payout.FAILED,
                failure_reason="Bank rejected payout",
            )

        else:
            retry_payout.apply_async((payout.id,), countdown=30)

    except Exception as e:
        print("Error processing payout:", str(e))


@shared_task(bind=True, max_retries=3)
def retry_payout(self, payout_id):
    try:
        payout = Payout.objects.get(id=payout_id)

        if payout.status != Payout.PROCESSING:
            return

        payout.attempts += 1
        payout.save()

        if payout.attempts >= 3:
            transition_payout_status(
                payout,
                Payout.FAILED,
                failure_reason="Max retries exceeded",
            )
            return

        retry_payout.apply_async(
            (payout.id,),
            countdown=2 ** payout.attempts,
        )

    except Exception as e:
        raise self.retry(exc=e, countdown=5)