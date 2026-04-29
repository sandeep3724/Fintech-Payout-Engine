# merchants/urls.py
from django.urls import path
from .views import MerchantDashboardView

urlpatterns = [
    path("<int:merchant_id>/dashboard/", MerchantDashboardView.as_view()),
]   