import uuid
from concurrent.futures import ThreadPoolExecutor

from django.test import TransactionTestCase, TestCase
from rest_framework.test import APIClient

from merchants.models import Merchant, BankAccount
from ledger.models import LedgerEntry
from payouts.models import Payout
from payouts.services import transition_payout_status


class PayoutConcurrencyTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.merchant = Merchant.objects.create(
            name="Concurrency Merchant",
            email="concurrency@test.com"
        )

        self.bank_account = BankAccount.objects.create(
            merchant=self.merchant,
            account_holder_name="Concurrency Merchant",
            bank_name="HDFC Bank",
            account_number="1234567890",
            ifsc_code="HDFC0001234"
        )

        LedgerEntry.objects.create(
            merchant=self.merchant,
            entry_type=LedgerEntry.CREDIT,
            amount_paise=10000,
            description="Seed credit"
        )

    def make_payout_request(self):
        client = APIClient()

        return client.post(
            "/api/v1/payouts/",
            {
                "merchant_id": self.merchant.id,
                "amount_paise": 6000,
                "bank_account_id": self.bank_account.id,
            },
            format="json",
            HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        )

    def test_two_simultaneous_payouts_only_one_succeeds(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(
                executor.map(lambda _: self.make_payout_request(), range(2))
            )

        status_codes = sorted([response.status_code for response in responses])

        self.assertEqual(status_codes, [201, 400])
        self.assertEqual(Payout.objects.count(), 1)

        successful_payout = Payout.objects.first()
        self.assertEqual(successful_payout.amount_paise, 6000)
        self.assertEqual(successful_payout.status, Payout.PENDING)


class PayoutStateMachineTest(TestCase):
    def setUp(self):
        self.merchant = Merchant.objects.create(
            name="State Merchant",
            email="state@test.com"
        )

        self.bank_account = BankAccount.objects.create(
            merchant=self.merchant,
            account_holder_name="State Merchant",
            bank_name="HDFC Bank",
            account_number="9876543210",
            ifsc_code="HDFC0009876"
        )

        self.payout = Payout.objects.create(
            merchant=self.merchant,
            bank_account=self.bank_account,
            amount_paise=5000,
            status=Payout.PENDING,
            idempotency_key="550e8400-e29b-41d4-a716-446655440099",
        )

    def test_failed_to_completed_is_blocked(self):
        # Move to processing
        transition_payout_status(self.payout, Payout.PROCESSING)
        self.payout.refresh_from_db()

        # Move to failed
        transition_payout_status(
            self.payout,
            Payout.FAILED,
            failure_reason="Bank failed"
        )
        self.payout.refresh_from_db()

        # Invalid transition: FAILED → COMPLETED
        with self.assertRaises(ValueError):
            transition_payout_status(self.payout, Payout.COMPLETED)