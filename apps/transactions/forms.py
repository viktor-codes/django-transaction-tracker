from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["type", "amount"]

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be positive")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get("type")
        amount = cleaned_data.get("amount")

        # Check balance for expenses
        if transaction_type == "expense" and amount:
            current_balance = Transaction.get_current_balance()
            if current_balance - amount < 0:
                raise forms.ValidationError("Not enough balance")

        return cleaned_data
