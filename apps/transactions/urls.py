from django.urls import path
from . import views

app_name = "transactions"

urlpatterns = [
    path("", views.transaction_list, name="transaction-list"),
    path(
        "load-transactions/", views.load_transactions, name="load-transactions"
    ),
    path("add-transaction/", views.add_transaction, name="add-transaction"),
    path(
        "edit-transaction/<int:pk>/",
        views.edit_transaction,
        name="edit-transaction",
    ),
    path(
        "load-more-transactions/",
        views.load_more_transactions,
        name="load-more-transactions",
    ),
]
