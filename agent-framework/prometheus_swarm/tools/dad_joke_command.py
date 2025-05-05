import requests
from typing import Dict, Any

def get_dad_joke() -> str:
    """
    Fetch a random dad joke from the icanhazdadjoke API.
    
    Returns:
        str: A dad joke text
    
    Raises:
        RuntimeError: If unable to fetch a dad joke
    """
    headers = {
        'Accept': 'text/plain',
        'User-Agent': 'Prometheus Swarm Dad Joke Command'
    }
    
    try:
        response = requests.get('https://icanhazdadjoke.com/', headers=headers)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch dad joke: {e}")

def dad_joke_command_handler(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle the dad joke command request.
    
    Args:
        args (Dict[str, Any]): Command arguments (not used in this implementation)
    
    Returns:
        Dict[str, Any]: A dictionary containing the dad joke
    """
    try:
        joke = get_dad_joke()
        return {
            'success': True,
            'message': joke
        }
    except RuntimeError as e:
        return {
            'success': False,
            'message': str(e)
        }