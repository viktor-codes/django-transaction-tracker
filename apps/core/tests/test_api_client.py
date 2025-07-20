from django.test import TestCase
from unittest.mock import patch, Mock
import requests
from apps.core.api_client import TransactionAPIClient


class TransactionAPIClientTest(TestCase):

    def setUp(self):
        self.client = TransactionAPIClient()
        self.sample_api_response = [
            {
                "createdAt": "2025-06-27T12:52:58.669Z",
                "amount": 41.42,
                "type": "expense",
                "id": "1"
            },
            {
                "createdAt": "2025-06-26T09:15:32.123Z",
                "amount": 75.80,
                "type": "deposit",
                "id": "2"
            }
        ]

    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_success(self, mock_get):
        """Test successful API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the method
        result = self.client.fetch_transactions()

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], '1')
        self.assertEqual(result[0]['amount'], 41.42)
        self.assertEqual(result[0]['type'], 'expense')
        self.assertEqual(result[1]['id'], '2')
        self.assertEqual(result[1]['amount'], 75.80)
        self.assertEqual(result[1]['type'], 'deposit')

        # Verify the correct URL was called
        expected_url = f"{self.client.BASE_URL}/transactions"
        mock_get.assert_called_once_with(expected_url)

    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_http_error(self, mock_get):
        """Test API call with HTTP error"""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        # Should raise RequestException
        with self.assertRaises(requests.RequestException):
            self.client.fetch_transactions()

    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_connection_error(self, mock_get):
        """Test API call with connection error"""
        # Mock connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        # Should raise RequestException
        with self.assertRaises(requests.RequestException):
            self.client.fetch_transactions()

    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_timeout(self, mock_get):
        """Test API call with timeout"""
        # Mock timeout error
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        # Should raise RequestException
        with self.assertRaises(requests.RequestException):
            self.client.fetch_transactions()

    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_invalid_json(self, mock_get):
        """Test API call with invalid JSON response"""
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Should raise ValueError
        with self.assertRaises(ValueError):
            self.client.fetch_transactions()

    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_empty_response(self, mock_get):
        """Test API call with empty response"""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the method
        result = self.client.fetch_transactions()

        # Should return empty list
        self.assertEqual(result, [])
        self.assertEqual(len(result), 0)

    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_server_error(self, mock_get):
        """Test API call with 500 server error"""
        # Mock server error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        # Should raise RequestException
        with self.assertRaises(requests.RequestException):
            self.client.fetch_transactions()

    @patch('apps.core.api_client.logger')
    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_logging(self, mock_get, mock_logger):
        """Test that successful calls are logged"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_api_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the method
        self.client.fetch_transactions()

        # Verify logging was called
        mock_logger.info.assert_called_with("Fetched 2 transactions from API")

    @patch('apps.core.api_client.logger')
    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_error_logging(self, mock_get, mock_logger):
        """Test that errors are logged"""
        # Mock connection error
        error_message = "Connection failed"
        mock_get.side_effect = requests.exceptions.ConnectionError(error_message)

        # Call should raise exception
        with self.assertRaises(requests.RequestException):
            self.client.fetch_transactions()

        # Verify error logging
        mock_logger.error.assert_called()
        # Check that the error was logged with the right message
        args, kwargs = mock_logger.error.call_args
        self.assertIn("Failed to fetch transactions", args[0])

    def test_base_url_configuration(self):
        """Test that BASE_URL is correctly configured"""
        expected_url = "https://685efce5c55df675589d49df.mockapi.io/api/v1"
        self.assertEqual(self.client.BASE_URL, expected_url)

    @patch('apps.core.api_client.requests.get')
    def test_fetch_transactions_malformed_data(self, mock_get):
        """Test API call with malformed transaction data"""
        # Mock response with malformed data
        malformed_response = [
            {
                "id": "1",
                "amount": "not_a_number",  # Invalid amount
                "type": "expense",
                "createdAt": "2025-06-27T12:52:58.669Z"
            }
        ]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = malformed_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Should still return the data (let the service layer handle validation)
        result = self.client.fetch_transactions()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['amount'], "not_a_number")