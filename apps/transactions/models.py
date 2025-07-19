from django.db import models
from apps.core.models import TimestampedModel


class Transaction(TimestampedModel):
    transaction_code = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=10, choices=[("deposit", "Deposit"), ("expense", "Expense")]
    )
    transaction_date = models.DateTimeField()

    class Meta:
        ordering = ['-transaction_date']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    @classmethod
    def get_current_balance(cls):
        """Calculate total current balance"""
        transactions = cls.objects.all()
        return sum(tx.get_signed_amount() for tx in transactions)

    def __str__(self):
        return f"{self.transaction_code} - {self.type} - ${self.amount}"
