from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from apps.transactions.models import Transaction


class TransactionModelTest(TestCase):

    def setUp(self):
        """Set up test data"""
        self.deposit_data = {
            "transaction_code": "TXN-0001",
            "amount": Decimal("100.00"),
            "type": "deposit",
            "transaction_date": timezone.now(),
        }

        self.expense_data = {
            "transaction_code": "TXN-0002",
            "amount": Decimal("50.00"),
            "type": "expense",
            "transaction_date": timezone.now(),
        }

    def test_create_deposit_transaction(self):
        """Test creating a deposit transaction"""
        transaction = Transaction.objects.create(**self.deposit_data)

        self.assertEqual(transaction.transaction_code, "TXN-0001")
        self.assertEqual(transaction.amount, Decimal("100.00"))
        self.assertEqual(transaction.type, "deposit")
        self.assertTrue(transaction.created_at)
        self.assertTrue(transaction.updated_at)

    def test_create_expense_transaction(self):
        """Test creating an expense transaction"""
        transaction = Transaction.objects.create(**self.expense_data)

        self.assertEqual(transaction.type, "expense")
        self.assertEqual(transaction.amount, Decimal("50.00"))

    def test_string_representation(self):
        """Test the string representation of a transaction"""
        transaction = Transaction.objects.create(**self.deposit_data)
        expected_str = "TXN-0001 - deposit - $100.00"
        self.assertEqual(str(transaction), expected_str)

    def test_get_signed_amount_deposit(self):
        """Test get_signed_amount for deposit returns positive"""
        transaction = Transaction.objects.create(**self.deposit_data)
        self.assertEqual(transaction.get_signed_amount(), Decimal("100.00"))

    def test_get_signed_amount_expense(self):
        """Test get_signed_amount for expense returns negative"""
        transaction = Transaction.objects.create(**self.expense_data)
        self.assertEqual(transaction.get_signed_amount(), Decimal("-50.00"))

    def test_get_current_balance(self):
        """Test get_current_balance class method"""
        # Create some transactions
        Transaction.objects.create(**self.deposit_data)  # +100
        Transaction.objects.create(**self.expense_data)  # -50
        Transaction.objects.create(
            transaction_code="TXN-0003",
            amount=Decimal("25.00"),
            type="deposit",
            transaction_date=timezone.now(),
        )  # +25

        balance = Transaction.get_current_balance()
        self.assertEqual(balance, Decimal("75.00"))  # 100 - 50 + 25

    def test_unique_transaction_code(self):
        """Test that transaction codes must be unique"""
        Transaction.objects.create(**self.deposit_data)

        # Try to create another transaction with same code
        with self.assertRaises(Exception):
            Transaction.objects.create(**self.deposit_data)
