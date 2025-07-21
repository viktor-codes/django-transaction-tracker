from django.test import TestCase, Client
from django.utils import timezone
from apps.transactions.models import Transaction
from decimal import Decimal


class TransactionViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        # Create test transactions
        self.deposit = Transaction.objects.create(
            transaction_code="TXN-0001",
            amount=Decimal("100.00"),
            type="deposit",
            transaction_date=timezone.now(),
        )

        self.expense = Transaction.objects.create(
            transaction_code="TXN-0002",
            amount=Decimal("30.00"),
            type="expense",
            transaction_date=timezone.now(),
        )

    def test_transaction_list_view(self):
        """Test the main transaction list view"""
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TXN-0001")
        self.assertContains(response, "TXN-0002")
        self.assertContains(response, "Balance: $70.00")  # 100 - 30

    def test_add_transaction_valid_deposit(self):
        """Test adding a valid deposit transaction"""
        response = self.client.post(
            "/add-transaction/", {"type": "deposit", "amount": "50.00"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Transaction added successfully")

        # Check transaction was created
        new_transaction = Transaction.objects.get(transaction_code="TXN-0003")
        self.assertEqual(new_transaction.amount, Decimal("50.00"))
        self.assertEqual(new_transaction.type, "deposit")

    def test_add_transaction_invalid_amount(self):
        """Test adding transaction with invalid amount"""
        response = self.client.post(
            "/add-transaction/", {"type": "deposit", "amount": "-50.00"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Amount must be positive")

        # Check no new transaction was created
        self.assertEqual(Transaction.objects.count(), 2)

    def test_load_more_transactions(self):
        """Test load more transactions endpoint"""
        # Create more transactions for pagination
        for i in range(15):
            Transaction.objects.create(
                transaction_code=f"TXN-{i + 100:04d}",
                amount=Decimal("10.00"),
                type="deposit",
                transaction_date=timezone.now(),
            )

        response = self.client.get("/load-more-transactions/?page=2")

        self.assertEqual(response.status_code, 200)
        # Should contain some transaction codes
        self.assertContains(response, "TXN-")
