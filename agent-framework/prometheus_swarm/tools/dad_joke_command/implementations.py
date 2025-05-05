import requests
from typing import Dict, Any

def get_dad_joke() -> Dict[str, Any]:
    """
    Fetch a random dad joke from the icanhazdadjoke API.
    
    Returns:
        Dict[str, Any]: A dictionary containing the dad joke details.
        Returns a dict with 'joke' and 'status' keys.
    """
    try:
        # Make a request to the icanhazdadjoke API
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Prometheus Swarm Dad Joke Command'
        }
        response = requests.get('https://icanhazdadjoke.com/', headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            joke_data = response.json()
            return {
                'joke': joke_data.get('joke', 'No joke found'),
                'status': 'success'
            }
        else:
            return {
                'joke': 'Failed to fetch dad joke',
                'status': 'error',
                'error_code': response.status_code
            }
    except requests.RequestException as e:
        return {
            'joke': 'Network error occurred while fetching dad joke',
            'status': 'error',
            'error': str(e)
        }