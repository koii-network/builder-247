import subprocess
import os
import requests
from prometheus_swarm.types import ToolOutput


# ... (previous existing implementations)


def get_dad_joke(**kwargs) -> ToolOutput:
    """
    Fetch and return a dad joke using an external API.
    
    Args:
        kwargs: Optional additional parameters (not used currently)
    
    Returns:
        ToolOutput with a dad joke
    """
    try:
        headers = {
            "Accept": "application/json"
        }
        response = requests.get("https://icanhazdadjoke.com/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            joke = response.json().get("joke", "No joke found")
            return {
                "success": True,
                "message": "Dad joke retrieved successfully",
                "data": {
                    "joke": joke
                }
            }
        else:
            return {
                "success": False,
                "message": f"Failed to retrieve dad joke. Status code: {response.status_code}",
                "data": None
            }
    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Error fetching dad joke: {str(e)}",
            "data": None
        }