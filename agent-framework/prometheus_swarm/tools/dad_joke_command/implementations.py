import requests
from typing import Dict, Any

def get_dad_joke() -> Dict[str, Any]:
    """
    Fetch a random dad joke from the icanhazdadjoke API.

    Returns:
        Dict[str, Any]: A dictionary containing the dad joke details
            - 'joke': The text of the dad joke
            - 'status': HTTP status code of the request
    """
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Prometheus Swarm Dad Joke Fetcher'
        }
        response = requests.get('https://icanhazdadjoke.com/', headers=headers)
        
        # Ensure successful request
        if response.status_code == 200:
            joke_data = response.json()
            return {
                'joke': joke_data.get('joke', 'No joke found'),
                'status': response.status_code
            }
        else:
            return {
                'joke': 'Failed to fetch dad joke',
                'status': response.status_code
            }
    except requests.RequestException as e:
        return {
            'joke': f'Error fetching dad joke: {str(e)}',
            'status': 500
        }