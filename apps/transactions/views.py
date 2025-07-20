from django.shortcuts import render
from .models import Transaction
from django.http import HttpResponse
from .services import TransactionService


def transaction_list(request):
    transactions = Transaction.objects.all().order_by(
        "transaction_date"
    )  # Oldest first for calculation

    # Calculate running balance
    running_balance = 0
    transactions_with_balance = []

    for transaction in transactions:
        if transaction.type == "deposit":
            running_balance += transaction.amount
        else:
            running_balance -= transaction.amount
        transaction.running_balance = running_balance
        transactions_with_balance.append(transaction)

    # Reverse to show newest first
    transactions_with_balance.reverse()

    return render(
        request,
        "transactions/index.html",
        {"transactions": transactions_with_balance, "current_balance": running_balance},
    )


def load_transactions(request):
    if request.method == "POST":
        try:
            created_count, skipped_count = (
                TransactionService.import_transactions_from_api()
            )

            # Return HTML response for HTMX
            return HttpResponse(
                f"""
                <div class="alert alert-success alert-dismissible fade show">
                    <strong>Success!</strong> Created: {created_count}, Skipped: {skipped_count}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                <script>
                    setTimeout(() => window.location.reload(), 2000);
                </script>
            """
            )

        except Exception as e:
            return HttpResponse(
                f"""
                <div class="alert alert-danger alert-dismissible fade show">
                    <strong>Error!</strong> {str(e)}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            """
            )
