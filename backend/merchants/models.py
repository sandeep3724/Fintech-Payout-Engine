from django.db import models

class Merchant(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)

    # 👇 THIS MUST EXIST
    balance_paise = models.BigIntegerField(default=0)

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="bank_accounts"
    )
    account_holder_name = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"