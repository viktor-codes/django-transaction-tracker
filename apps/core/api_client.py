import requests
import logging

logger = logging.getLogger(__name__)


class TransactionAPIClient:
    BASE_URL = "https://685efce5c55df675589d49df.mockapi.io/api/v1"

    def fetch_transactions(self):
        """
        Fetch transactions from external API
        Returns list of transaction data or raises exception
        """
        try:
            response = requests.get(f"{self.BASE_URL}/transactions")
            response.raise_for_status()

            transactions_data = response.json()
            logger.info(
                f"Fetched {len(transactions_data)} transactions from API"
            )

            return transactions_data

        except requests.RequestException as e:
            logger.error(f"Failed to fetch transactions: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise
