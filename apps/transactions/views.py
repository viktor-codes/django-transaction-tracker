from django.shortcuts import render
from .models import Transaction
from django.http import HttpResponse
from .services import TransactionService
from .forms import TransactionForm
from django.utils import timezone
from django.core.paginator import Paginator


def _calculate_running_balances(transactions):
    """Helper function to calculate running balances for transactions"""
    running_balance = 0
    transactions_with_balance = []

    for transaction in transactions:
        if transaction.type == "deposit":
            running_balance += transaction.amount
        else:
            running_balance -= transaction.amount
        transaction.running_balance = running_balance
        transactions_with_balance.append(transaction)

    return transactions_with_balance, running_balance


def _get_paginated_transactions(page_number=1):
    """Helper function to get paginated transactions with running balances"""
    transactions = Transaction.objects.all().order_by("transaction_date")

    # Calculate running balance
    transactions_with_balance, total_balance = _calculate_running_balances(transactions)

    # Reverse to show newest first
    transactions_with_balance.reverse()

    # Paginate
    paginator = Paginator(transactions_with_balance, 10)
    page_obj = paginator.get_page(page_number)

    return page_obj, total_balance


def transaction_list(request):
    page_number = request.GET.get("page", 1)
    page_obj, current_balance = _get_paginated_transactions(page_number)

    return render(
        request,
        "transactions/index.html",
        {
            "transactions": page_obj,
            "current_balance": current_balance,
            "has_more": page_obj.has_next(),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        },
    )


def load_transactions(request):
    if request.method == "POST":
        try:
            created_count, skipped_count = TransactionService.import_transactions_from_api()

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


def load_more_transactions(request):
    """AJAX endpoint for loading more transactions"""
    page_number = int(request.GET.get("page", 2))
    page_obj, _ = _get_paginated_transactions(page_number)

    return render(
        request,
        "transactions/partials/transaction_rows.html",
        {
            "transactions": page_obj,
            "has_more": page_obj.has_next(),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
        },
    )


def _generate_transaction_code():
    """Generate next available transaction code"""
    count = Transaction.objects.count()
    return f"TXN-{count + 1:04d}"


def _create_alert_response(message, alert_type="success", auto_close=False):
    """Helper function to create alert responses"""
    auto_close_script = ""
    if auto_close:
        auto_close_script = """
        <script>
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('addTransactionModal')).hide();
                window.location.reload();
            }, 1500);
        </script>
        """

    return HttpResponse(f"""
        <div class="alert alert-{alert_type} alert-dismissible">
            {message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {auto_close_script}
    """)


def add_transaction(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)

        if form.is_valid():
            try:
                # Create transaction
                transaction = form.save(commit=False)
                transaction.transaction_code = _generate_transaction_code()
                transaction.transaction_date = timezone.now()
                transaction.save()

                return _create_alert_response(
                    "Transaction added successfully!",
                    "success",
                    auto_close=True
                )

            except Exception as e:
                return _create_alert_response(
                    f"Error creating transaction: {str(e)}",
                    "danger"
                )
        else:
            # Return form errors
            error_messages = []
            for field, errors in form.errors.items():
                error_messages.extend(errors)

            return _create_alert_response(
                "<br>".join(error_messages),
                "danger"
            )