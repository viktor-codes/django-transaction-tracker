from django import forms
from .models import Transaction
from datetime import date


class TransactionForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=[("deposit", "Deposit"), ("expense", "Expense")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Transaction
        fields = ["type", "amount"]
        widgets = {
            "amount": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0.01"}
            )
        }

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
                # Check daily expense limit (200 expenses per day)
            if transaction_type == "expense":
                today = date.today()
                today_expenses_count = Transaction.objects.filter(
                    type="expense", transaction_date__date=today
                ).count()

                if today_expenses_count >= 200:
                    raise (
                        forms.ValidationError(
                            "Your daily expense limit reached."
                        )
                    )

        return cleaned_data
