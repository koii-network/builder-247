"""Definitions for Dad Joke Command Handler."""

from typing import Dict, Any

def dad_joke_command_definition() -> Dict[str, Any]:
    """
    Define the Dad Joke command tool.
    
    Returns:
        Dict: Tool definition for the Dad Joke command
    """
    return {
        "type": "function",
        "function": {
            "name": "get_dad_joke_command",
            "description": "Get a random dad joke from the internet or offline collection",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }