"""Dad Joke Client Module.

This module provides a client for retrieving and interacting with Dad Jokes.
"""

import requests
from typing import Dict, Optional, Any
from .dadjoke_logger import DadJokeLogger, track_joke_performance

class DadJokeClient:
    """Client for retrieving and managing Dad Jokes."""

    API_BASE_URL = "https://icanhazdadjoke.com/"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dad Joke Client.

        Args:
            api_key (Optional[str]): Optional API key for advanced features
        """
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Prometheus Swarm Agent (github.com/your-org/prometheus-swarm)"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    @track_joke_performance
    def get_random_joke(self) -> Dict[str, Any]:
        """
        Retrieve a random dad joke from the API.

        Returns:
            Dict[str, Any]: Joke details including ID and joke text
        """
        try:
            response = requests.get(self.API_BASE_URL, headers=self.headers)
            response.raise_for_status()
            joke_data = response.json()

            # Log joke retrieval
            DadJokeLogger.log_joke_retrieval(
                joke=joke_data.get('joke', ''),
                source='icanhazdadjoke.com',
                retrieval_method='random_api_call',
                metadata={
                    'joke_id': joke_data.get('id'),
                    'status_code': response.status_code
                }
            )

            return joke_data

        except requests.RequestException as e:
            # Log error in joke retrieval
            DadJokeLogger.log_joke_error(
                error=e,
                context='Random Joke Retrieval',
                joke_details={'api_url': self.API_BASE_URL}
            )
            raise

    def rate_joke(self, joke_id: str, rating: int) -> Dict[str, Any]:
        """
        Rate a dad joke.

        Args:
            joke_id (str): ID of the joke to rate
            rating (int): Rating value (e.g., 1-5)

        Returns:
            Dict[str, Any]: Rating submission result
        """
        try:
            # Simulated rating mechanism (replace with actual implementation)
            rating_result = {
                'joke_id': joke_id,
                'rating': rating,
                'success': True
            }

            # Log joke interaction
            DadJokeLogger.log_joke_interaction(
                interaction_type='rating',
                joke=f'Joke ID: {joke_id}',
                user_response={
                    'rating': rating,
                    'success': rating_result['success']
                }
            )

            return rating_result

        except Exception as e:
            # Log error in joke rating
            DadJokeLogger.log_joke_error(
                error=e,
                context='Joke Rating',
                joke_details={'joke_id': joke_id, 'rating': rating}
            )
            raise