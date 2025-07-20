from django.test import TestCase
from apps.transactions.forms import TransactionForm
from apps.transactions.models import Transaction
from decimal import Decimal
from django.utils import timezone


class TransactionFormTest(TestCase):

    def test_valid_deposit_form(self):
        """Test form with valid deposit data"""
        form_data = {
            'type': 'deposit',
            'amount': '100.00'
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_expense_form(self):
        """Test form with valid expense data"""
        # Create initial balance
        Transaction.objects.create(
            transaction_code='TXN-0001',
            amount=Decimal('200.00'),
            type='deposit',
            transaction_date=timezone.now()
        )

        form_data = {
            'type': 'expense',
            'amount': '50.00'
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_negative_amount_validation(self):
        """Test that negative amounts are rejected"""
        form_data = {
            'type': 'deposit',
            'amount': '-50.00'
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Amount must be positive', str(form.errors))

    def test_zero_amount_validation(self):
        """Test that zero amounts are rejected"""
        form_data = {
            'type': 'deposit',
            'amount': '0.00'
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Amount must be positive', str(form.errors))

    def test_insufficient_balance_validation(self):
        """Test validation for insufficient balance"""
        # Create small initial balance
        Transaction.objects.create(
            transaction_code='TXN-0001',
            amount=Decimal('10.00'),
            type='deposit',
            transaction_date=timezone.now()
        )

        form_data = {
            'type': 'expense',
            'amount': '50.00'  # More than available balance
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Not enough balance', str(form.errors))

    def test_daily_expense_limit_validation(self):
        """Test daily expense limit validation"""
        # Create initial balance
        Transaction.objects.create(
            transaction_code='TXN-0001',
            amount=Decimal('10000.00'),
            type='deposit',
            transaction_date=timezone.now()
        )

        # Create 200 expenses today
        today = timezone.now()
        for i in range(200):
            Transaction.objects.create(
                transaction_code=f'TXN-{i + 2:04d}',
                amount=Decimal('1.00'),
                type='expense',
                transaction_date=today
            )

        # Try to create 201st expense
        form_data = {
            'type': 'expense',
            'amount': '1.00'
        }
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Your daily expense limit reached', str(form.errors))