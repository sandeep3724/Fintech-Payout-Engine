import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from merchants.models import Merchant, BankAccount
from ledger.models import LedgerEntry


def seed():
    merchant, _ = Merchant.objects.get_or_create(
        email="merchant@playto.so",
        defaults={
            "name": "Playto Demo Merchant",
        },
    )

    BankAccount.objects.get_or_create(
        merchant=merchant,
        account_number="1234567890",
        defaults={
            "account_holder_name": "Playto Demo Merchant",
            "bank_name": "HDFC Bank",
            "ifsc_code": "HDFC0001234",
        },
    )

    if not LedgerEntry.objects.filter(
        merchant=merchant,
        reference_id="seed-credit-1"
    ).exists():
        LedgerEntry.objects.create(
            merchant=merchant,
            entry_type=LedgerEntry.CREDIT,
            amount_paise=100000,
            description="Seed customer payment",
            reference_id="seed-credit-1",
        )

    print("Seed completed successfully")
    print("Merchant ID:", merchant.id)


seed()