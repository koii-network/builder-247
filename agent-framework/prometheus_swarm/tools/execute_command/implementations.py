import subprocess
import os
import requests
from prometheus_swarm.types import ToolOutput

# ... [rest of the existing code remains the same, adding get_dad_joke function at the end]

def get_dad_joke(**kwargs) -> ToolOutput:
    """
    Fetch a random dad joke from the icanhazdadjoke API.

    Returns:
        ToolOutput: A standardized output containing the dad joke
    """
    try:
        headers = {
            "Accept": "application/json",
            "User-Agent": "OrcaAI (https://github.com/your-github-repo)"
        }
        response = requests.get("https://icanhazdadjoke.com/", headers=headers)
        
        if response.status_code == 200:
            joke_data = response.json()
            joke = joke_data.get('joke', 'No joke found.')
            
            return {
                "success": True,
                "message": "Dad joke fetched successfully",
                "data": {
                    "joke": joke,
                    "status_code": response.status_code
                }
            }
        else:
            return {
                "success": False,
                "message": f"Failed to fetch dad joke. Status code: {response.status_code}",
                "data": {
                    "status_code": response.status_code
                }
            }
    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Error fetching dad joke: {str(e)}",
            "data": {
                "error": str(e)
            }
        }