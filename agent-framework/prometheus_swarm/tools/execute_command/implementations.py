import subprocess
import os
import requests
from prometheus_swarm.types import ToolOutput

# Existing code for execute_command, run_tests, install_dependency, and setup_dependencies functions

def get_dad_joke(category: str = "random", **kwargs) -> ToolOutput:
    """
    Retrieve a random dad joke, with optional category filtering.
    
    Args:
        category: Optional dad joke category (coding, general, pun, random)
    
    Returns:
        ToolOutput: Standardized tool output with dad joke
    """
    try:
        joke_categories = {
            "coding": "programming",
            "general": "general",
            "pun": "pun",
            "random": None
        }
        
        if category not in joke_categories:
            return {
                "success": False,
                "message": f"Invalid category. Choose from {list(joke_categories.keys())}",
                "data": None
            }
        
        # Use icanhazdadjoke.com API
        headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Dad Joke Tool"
        }
        
        if joke_categories[category]:
            response = requests.get(
                f"https://icanhazdadjoke.com/search?term={joke_categories[category]}",
                headers=headers
            )
        else:
            response = requests.get(
                "https://icanhazdadjoke.com/",
                headers=headers
            )
        
        response.raise_for_status()
        
        if "search" in response.url:
            # For search results, pick a random joke
            jokes = response.json().get('results', [])
            if not jokes:
                return {
                    "success": False,
                    "message": f"No jokes found for category: {category}",
                    "data": None
                }
            joke = jokes[0]['joke']
        else:
            # For random joke
            joke = response.json().get('joke')
        
        return {
            "success": True,
            "message": "Dad joke retrieved successfully",
            "data": {
                "joke": joke,
                "category": category
            }
        }
    
    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"Failed to retrieve dad joke: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error retrieving dad joke: {str(e)}",
            "data": None
        }