from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_code",
        "type",
        "amount",
        "transaction_date",
        "created_at",
    ]
    list_filter = ["type", "created_at"]
    search_fields = ["transaction_code"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-transaction_date"]
