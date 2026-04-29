from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("🚀 Fintech Payout Engine Running")

urlpatterns = [
    path('', home),  # optional but useful
    path('admin/', admin.site.urls),

    # 👇 THIS IS WHAT YOU ARE MISSING
    path('api/', include('payouts.urls')),
]