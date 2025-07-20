from django.utils.dateparse import parse_datetime
from .models import Transaction
from apps.core.api_client import TransactionAPIClient
import logging

logger = logging.getLogger(__name__)


class TransactionService:

    @staticmethod
    def import_transactions_from_api():
        """
        Import transactions from external API and save to database
        Returns tuple: (created_count, skipped_count)
        """
        api_client = TransactionAPIClient()

        try:
            # Fetch from API
            api_transactions = api_client.fetch_transactions()

            created_count = 0
            skipped_count = 0

            for transaction_data in api_transactions:
                # Check if transaction already exists
                if Transaction.objects.filter(
                    transaction_code=transaction_data["id"]
                ).exists():
                    skipped_count += 1
                    continue

                # Create new transaction
                transaction = Transaction(
                    transaction_code=transaction_data["id"],
                    amount=abs(transaction_data["amount"]),
                    type=transaction_data["type"],
                    transaction_date=parse_datetime(
                        transaction_data["createdAt"]
                    ),
                )

                transaction.save()
                created_count += 1

            logger.info(
                f"Import complete: {created_count} created, {skipped_count} skipped"
            )
            return created_count, skipped_count

        except Exception as e:
            logger.error(f"Transaction import failed: {e}")
            raise
