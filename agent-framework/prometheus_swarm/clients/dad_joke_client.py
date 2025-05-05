import requests

class DadJokeClient:
    """
    A client for fetching dad jokes from the icanhazdadjoke API.
    """
    BASE_URL = "https://icanhazdadjoke.com/"

    @classmethod
    def get_random_joke(cls) -> str:
        """
        Fetch a random dad joke from the icanhazdadjoke API.

        Returns:
            str: A random dad joke.

        Raises:
            requests.RequestException: If there's an error fetching the joke.
            ValueError: If no joke is returned or the response is invalid.
        """
        try:
            response = requests.get(
                cls.BASE_URL, 
                headers={
                    "Accept": "text/plain",
                    "User-Agent": "Prometheus Swarm Dad Joke Client"
                },
                timeout=10  # Add a timeout to prevent hanging
            )
            # Explicitly check status before processing
            if response.status_code != 200:
                raise requests.RequestException(f"HTTP error {response.status_code}")

            joke = response.text.strip()
            if not joke:
                raise ValueError("No joke received from the API")

            return joke
        except Exception as e:
            raise requests.RequestException(f"Error fetching dad joke: {e}")