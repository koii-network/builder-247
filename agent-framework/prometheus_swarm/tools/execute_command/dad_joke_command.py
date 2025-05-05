import requests
from typing import Dict, Any

def get_dad_joke() -> Dict[str, Any]:
    """
    Fetch a random dad joke from the icanhazdadjoke API.

    Returns:
        Dict[str, Any]: A dictionary containing the dad joke details
    """
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Prometheus Swarm Dad Joke Generator'
        }
        response = requests.get('https://icanhazdadjoke.com/', headers=headers)
        response.raise_for_status()
        joke_data = response.json()
        return {
            'status': 'success',
            'joke': joke_data.get('joke', 'No joke found'),
            'id': joke_data.get('id', '')
        }
    except requests.RequestException as e:
        return {
            'status': 'error',
            'message': f'Failed to fetch dad joke: {str(e)}'
        }

def dad_joke_command_handler(args: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Command handler for retrieving a random dad joke.

    Args:
        args (Dict[str, Any], optional): Optional arguments (not used in this implementation)

    Returns:
        Dict[str, Any]: A dictionary containing the dad joke or error information
    """
    joke_result = get_dad_joke()
    return joke_result