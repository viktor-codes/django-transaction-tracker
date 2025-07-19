from django.shortcuts import render
from .models import Transaction


def transaction_list(request):
    transactions = Transaction.objects.all().order_by("-transaction_date")
    return render(request, "transactions/index.html", {"transactions": transactions})
