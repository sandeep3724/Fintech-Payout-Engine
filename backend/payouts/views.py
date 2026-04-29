from uuid import UUID

from django.db import IntegrityError, transaction
from django.db.transaction import on_commit
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from merchants.models import BankAccount, Merchant
from ledger.models import LedgerEntry
from ledger.services import get_available_balance_paise

from .models import Payout
from .serializers import PayoutCreateSerializer, PayoutSerializer
from .tasks import process_payout


@method_decorator(csrf_exempt, name="dispatch")
class PayoutCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response(
                {"error": "Idempotency-Key header is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            UUID(idempotency_key)
        except ValueError:
            return Response(
                {"error": "Idempotency-Key must be a valid UUID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PayoutCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        merchant_id = serializer.validated_data["merchant_id"]
        amount_paise = serializer.validated_data["amount_paise"]
        bank_account_id = serializer.validated_data["bank_account_id"]

        try:
            with transaction.atomic():
                merchant = Merchant.objects.select_for_update().get(id=merchant_id)

                existing_payout = Payout.objects.filter(
                    merchant=merchant,
                    idempotency_key=idempotency_key,
                ).first()

                if existing_payout:
                    return Response(
                        PayoutSerializer(existing_payout).data,
                        status=status.HTTP_200_OK,
                    )

                bank_account = BankAccount.objects.get(
                    id=bank_account_id,
                    merchant=merchant,
                )

                available_balance = get_available_balance_paise(merchant)

                if available_balance < amount_paise:
                    return Response(
                        {
                            "error": "Insufficient balance",
                            "available_balance_paise": available_balance,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                payout = Payout.objects.create(
                    merchant=merchant,
                    bank_account=bank_account,
                    amount_paise=amount_paise,
                    status=Payout.PENDING,
                    idempotency_key=idempotency_key,
                )

                LedgerEntry.objects.create(
                    merchant=merchant,
                    entry_type=LedgerEntry.DEBIT,
                    amount_paise=amount_paise,
                    description=f"Funds held for payout #{payout.id}",
                    reference_id=f"payout:{payout.id}",
                )

                def enqueue_payout():
    try:
        process_payout.delay(payout.id)
    except Exception as e:
        print("Celery enqueue failed:", str(e))

on_commit(enqueue_payout)

                return Response(
                    PayoutSerializer(payout).data,
                    status=status.HTTP_201_CREATED,
                )

        except Merchant.DoesNotExist:
            return Response(
                {"error": "Merchant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except BankAccount.DoesNotExist:
            return Response(
                {"error": "Bank account not found for this merchant"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except IntegrityError:
            payout = Payout.objects.get(
                merchant_id=merchant_id,
                idempotency_key=idempotency_key,
            )

            return Response(
                PayoutSerializer(payout).data,
                status=status.HTTP_200_OK,
            )


class PayoutDetailView(RetrieveAPIView):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer


@api_view(["GET"])
def merchant_dashboard(request, merchant_id):
    try:
        merchant = Merchant.objects.get(id=merchant_id)
    except Merchant.DoesNotExist:
        return Response(
            {"error": "Merchant not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    available_balance = get_available_balance_paise(merchant)

    payouts = Payout.objects.filter(
        merchant=merchant
    ).order_by("-created_at")[:10]

    ledger_entries = LedgerEntry.objects.filter(
        merchant=merchant
    ).order_by("-created_at")[:10]

    held_balance = sum(
        payout.amount_paise
        for payout in Payout.objects.filter(
            merchant=merchant,
            status__in=[Payout.PENDING, Payout.PROCESSING],
        )
    )

    return Response(
        {
            "merchant": {
                "id": merchant.id,
                "name": merchant.name,
                "email": merchant.email,
            },
            "available_balance_paise": available_balance,
            "held_balance_paise": held_balance,
            "ledger_entries": [
                {
                    "id": entry.id,
                    "entry_type": entry.entry_type,
                    "amount_paise": entry.amount_paise,
                    "description": entry.description,
                    "created_at": entry.created_at,
                }
                for entry in ledger_entries
            ],
            "payouts": PayoutSerializer(payouts, many=True).data,
        }
    )