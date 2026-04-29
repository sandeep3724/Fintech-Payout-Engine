from django.urls import path
from .views import create_payout, merchant_dashboard

urlpatterns = [
    path("payouts/", create_payout),
    path("merchants/<int:merchant_id>/dashboard/", merchant_dashboard),
]