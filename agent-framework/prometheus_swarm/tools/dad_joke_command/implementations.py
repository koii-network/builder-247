"""Implementations for Dad Joke Command Handler."""

import requests
import random

def get_dad_joke():
    """
    Fetch a dad joke from the icanhazdadjoke API.
    
    Returns:
        str: A random dad joke
    
    Raises:
        RequestException: If there's an issue fetching the joke
    """
    headers = {"Accept": "application/json"}
    url = "https://icanhazdadjoke.com/"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["joke"]
    except Exception as e:
        return f"Joke machine broke: {str(e)}"

def generate_offline_dad_joke():
    """
    Generate an offline dad joke when API is unavailable.
    
    Returns:
        str: A pre-defined dad joke
    """
    offline_jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "I'm afraid for the calendar. Its days are numbered."
    ]
    return random.choice(offline_jokes)

def get_dad_joke_command():
    """
    Main command handler for fetching a dad joke.
    
    Returns:
        str: A dad joke from online API or offline collection
    """
    try:
        return get_dad_joke()
    except Exception:
        return generate_offline_dad_joke()