import requests
import json
from ..utils.errors import NetworkError, APIError, handle_api_error

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
            response = requests.request(method, url, **kwargs)
            
            # Check for API-level errors
            handle_api_error(response)
            
            # Attempt to parse JSON response
            try:
                return response.json()
            except ValueError:
                raise APIError("Malformed response: Unable to parse JSON")
        
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Unable to connect: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timed out: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {str(e)}")