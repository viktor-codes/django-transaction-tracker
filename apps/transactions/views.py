# In apps/transactions/views.py
from django.shortcuts import render
from .models import Transaction


def transaction_list(request):
    transactions = Transaction.objects.all().order_by(
        "transaction_date"
    )  # Oldest first for calculation

    # Calculate running balance
    running_balance = 0
    transactions_with_balance = []

    for transaction in transactions:
        running_balance += transaction.amount
        transaction.running_balance = running_balance
        transactions_with_balance.append(transaction)

    # Reverse to show newest first
    transactions_with_balance.reverse()

    return render(
        request,
        "transactions/index.html",
        {"transactions": transactions_with_balance, "current_balance": running_balance},
    )
