import subprocess
import os
import requests
from prometheus_swarm.types import ToolOutput

# Previous implementations remain the same...

def get_dad_joke() -> ToolOutput:
    """Fetch a random dad joke from icanhazdadjoke.com.

    Returns:
        ToolOutput: A dictionary containing the fetched dad joke
    """
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Prometheus Swarm Dad Joke Fetcher (https://github.com/yourusername/project)'
        }
        response = requests.get('https://icanhazdadjoke.com/', headers=headers)
        
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"Failed to fetch dad joke. Status code: {response.status_code}",
                "data": None
            }
        
        joke = response.json().get('joke')
        if not joke:
            return {
                "success": False,
                "message": "No joke found in the response",
                "data": None
            }
        
        return {
            "success": True,
            "message": joke,
            "data": {
                "joke": joke
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error fetching dad joke: {str(e)}",
            "data": None
        }