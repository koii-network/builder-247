import subprocess
import os
import requests
from prometheus_swarm.types import ToolOutput  # Add this import

# Rest of the existing implementation follows...

def get_dad_joke(**kwargs) -> ToolOutput:
    """
    Fetch a random dad joke from the icanhazdadjoke API.

    Args:
        kwargs: Optional keyword arguments (not used, for compatibility)

    Returns:
        ToolOutput: A dictionary containing the joke details
    """
    try:
        headers = {"Accept": "application/json"}
        response = requests.get("https://icanhazdadjoke.com/", headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"Failed to fetch dad joke. Status code: {response.status_code}",
                "data": None
            }
        
        joke_data = response.json()
        
        return {
            "success": True,
            "message": "Dad joke fetched successfully",
            "data": {
                "joke": joke_data.get("joke", "No joke found"),
                "id": joke_data.get("id"),
            }
        }
    
    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Error fetching dad joke: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "data": None
        }