from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import PayoutCreateView, PayoutDetailView, merchant_dashboard

urlpatterns = [
    path("payouts/", csrf_exempt(PayoutCreateView.as_view()), name="create-payout"),
    path("payouts/<int:pk>/", PayoutDetailView.as_view(), name="payout-detail"),
    path("merchants/<int:merchant_id>/dashboard/", merchant_dashboard, name="merchant-dashboard"),
]