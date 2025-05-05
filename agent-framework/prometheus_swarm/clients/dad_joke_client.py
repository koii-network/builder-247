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
                }
            )
            response.raise_for_status()  # Raise an exception for bad status codes

            joke = response.text.strip()
            if not joke:
                raise ValueError("No joke received from the API")

            return joke
        except requests.RequestException as e:
            raise requests.RequestException(f"Error fetching dad joke: {e}")