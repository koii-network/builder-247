import requests
import json
from ..utils.errors import NetworkError, APIError, AuthenticationError, RateLimitError

class BaseClient:
    """Base client for API interactions with robust error handling."""

    def __init__(self, base_url=None, api_key=None, timeout=30):
        """
        Initialize the base client.
        
        Args:
            base_url (str, optional): Base URL for API requests
            api_key (str, optional): API authentication key
            timeout (int, optional): Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def _make_request(self, method, url, **kwargs):
        """
        Make an HTTP request with comprehensive error handling.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            url (str): Request URL
            **kwargs: Additional request parameters
        
        Returns:
            The parsed JSON response
        
        Raises:
            NetworkError: For connection and timeout issues
            APIError: For server-side and parsing errors
        """
        headers = kwargs.get('headers', {})
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        kwargs['headers'] = headers
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)

        try:
            try:
                response = requests.request(method, url, **kwargs)
            except (requests.exceptions.ConnectionError, ConnectionError) as e:
                raise NetworkError(f"Unable to connect: {str(e)}")
            except (requests.exceptions.Timeout, TimeoutError) as e:
                raise NetworkError(f"Request timed out: {str(e)}")

            # Handle HTTP status code errors
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif 400 <= response.status_code < 600:
                raise APIError(f"Server error: {response.status_code} - {response.text}")

            # Attempt to parse JSON response
            try:
                return response.json()
            except ValueError:
                raise APIError("Malformed response: Unable to parse JSON")

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {str(e)}")