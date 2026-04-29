from django.urls import path
from .views import PayoutCreateView, merchant_dashboard

urlpatterns = [
    path("payouts/", PayoutCreateView.as_view(), name="create-payout"),
    path("merchants/<int:merchant_id>/dashboard/", merchant_dashboard, name="merchant-dashboard"),
]