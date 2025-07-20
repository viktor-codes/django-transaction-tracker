from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.transactions.services import TransactionService
from apps.transactions.models import Transaction


class TransactionServiceTest(TestCase):

    @patch("apps.transactions.services.TransactionAPIClient")
    def test_import_transactions_success(self, mock_api_client):
        """Test successful transaction import from API"""
        # Mock API response
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        mock_client_instance.fetch_transactions.return_value = [
            {
                "id": "API-001",
                "amount": 100.50,
                "type": "deposit",
                "createdAt": "2025-07-20T10:00:00Z",
            },
            {
                "id": "API-002",
                "amount": 50.25,
                "type": "expense",
                "createdAt": "2025-07-20T11:00:00Z",
            },
        ]

        created_count, skipped_count = (
            TransactionService.import_transactions_from_api()
        )

        self.assertEqual(created_count, 2)
        self.assertEqual(skipped_count, 0)
        self.assertEqual(Transaction.objects.count(), 2)

        # Check first transaction
        deposit = Transaction.objects.get(transaction_code="API-001")
        self.assertEqual(deposit.amount, 100.50)
        self.assertEqual(deposit.type, "deposit")

        # Check second transaction
        expense = Transaction.objects.get(transaction_code="API-002")
        self.assertEqual(expense.amount, 50.25)
        self.assertEqual(expense.type, "expense")

    @patch("apps.transactions.services.TransactionAPIClient")
    def test_import_transactions_skip_duplicates(self, mock_api_client):
        """Test that duplicate transactions are skipped"""
        # Create existing transaction
        Transaction.objects.create(
            transaction_code="API-001",
            amount=100.00,
            type="deposit",
            transaction_date="2025-07-20T10:00:00Z",
        )

        # Mock API response with same transaction
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        mock_client_instance.fetch_transactions.return_value = [
            {
                "id": "API-001",  # Same ID as existing
                "amount": 100.50,
                "type": "deposit",
                "createdAt": "2025-07-20T10:00:00Z",
            }
        ]

        created_count, skipped_count = (
            TransactionService.import_transactions_from_api()
        )

        self.assertEqual(created_count, 0)
        self.assertEqual(skipped_count, 1)
        self.assertEqual(Transaction.objects.count(), 1)  # Still only one

    @patch("apps.transactions.services.TransactionAPIClient")
    def test_import_transactions_api_error(self, mock_api_client):
        """Test handling of API errors"""
        mock_client_instance = MagicMock()
        mock_api_client.return_value = mock_client_instance
        mock_client_instance.fetch_transactions.side_effect = Exception(
            "API Error"
        )

        with self.assertRaises(Exception):
            TransactionService.import_transactions_from_api()
