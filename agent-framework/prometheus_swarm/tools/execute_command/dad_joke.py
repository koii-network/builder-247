import requests
from typing import Dict, Any

def get_dad_joke(**kwargs) -> Dict[str, Any]:
    """
    Fetch a random dad joke from the icanhazdadjoke.com API.

    Returns:
        A dictionary with the joke details in the standard ToolOutput format.
    """
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Prometheus Swarm Dad Joke Fetcher (https://github.com/your_repo)'
        }
        response = requests.get('https://icanhazdadjoke.com/', headers=headers, timeout=10)
        
        if response.status_code == 200:
            joke = response.json()['joke']
            return {
                "success": True,
                "message": joke,
                "data": {
                    "joke": joke
                }
            }
        else:
            return {
                "success": False,
                "message": f"Failed to fetch dad joke. Status code: {response.status_code}",
                "data": None
            }
    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Error fetching dad joke: {str(e)}",
            "data": None
        }