from django.urls import path
from . import views

urlpatterns = [
    path('', views.payout_list),   # example
]