from django.urls import path
from . import views

app_name = "transactions"

urlpatterns = [
    path("", views.transaction_list, name="transaction-list"),
    path("load-transactions/", views.load_transactions, name="load-transactions"),
]
