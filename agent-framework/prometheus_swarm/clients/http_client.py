import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

class HttpClient:
    """
    A robust HTTP client utility for making API requests with enhanced error handling and configuration.
    """

    @staticmethod
    def make_request(
        url: str,
        method: str = 'GET',
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with comprehensive error handling and configuration.

        Args:
            url (str): The URL to send the request to.
            method (str, optional): HTTP method. Defaults to 'GET'.
            headers (dict, optional): HTTP headers to send with the request.
            params (dict, optional): URL parameters to append to the request.
            data (dict, optional): Form-encoded data to send in the request body.
            json (dict, optional): JSON data to send in the request body.
            timeout (int, optional): Request timeout in seconds. Defaults to 30.
            verify_ssl (bool, optional): Verify SSL certificate. Defaults to True.

        Returns:
            dict: Response data from the server.

        Raises:
            ValueError: If the method is not supported.
            ConnectionError: If there's a network connectivity issue.
            Timeout: If the request times out.
            HTTPError: If the server returns an error status code.
        """
        # Validate method
        method = method.upper()
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        if method not in valid_methods:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Default headers
        default_headers = {
            'Accept': 'application/json',
            'User-Agent': 'Prometheus Swarm HTTP Client'
        }
        headers = {**default_headers, **(headers or {})}

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=timeout,
                verify=verify_ssl
            )

            # Raise an HTTPError for bad status codes
            response.raise_for_status()

            # Return JSON if possible, otherwise text
            try:
                return response.json()
            except ValueError:
                return {'text': response.text}

        except Timeout:
            raise Timeout(f"Request to {url} timed out after {timeout} seconds")
        except ConnectionError:
            raise ConnectionError(f"Could not connect to {url}")
        except HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.reason}"
            raise HTTPError(error_msg)
        except RequestException as e:
            raise RequestException(f"Unexpected error during request: {str(e)}")