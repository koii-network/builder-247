from typing import Dict, Any

def get_dad_joke_command_definition() -> Dict[str, Any]:
    """
    Define the dad joke command for the tool registry.

    Returns:
        Dict[str, Any]: Command definition for the dad joke handler
    """
    return {
        "name": "get_dad_joke",
        "description": "Fetch a random dad joke from icanhazdadjoke.com",
        "parameters": {},
        "implementation": "prometheus_swarm.tools.dad_joke_command.implementations.get_dad_joke"
    }