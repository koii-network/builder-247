import random

class DadJokeService:
    def __init__(self):
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "I'm afraid for the calendar. Its days are numbered.",
            "Why don't eggs tell jokes? They'd crack each other up!"
        ]

    def get_random_joke(self):
        """
        Returns a random dad joke from the collection.
        
        Returns:
            str: A random dad joke
        """
        if not self.jokes:
            raise ValueError("No jokes available")
        return random.choice(self.jokes)

    def add_joke(self, joke):
        """
        Adds a new joke to the collection.
        
        Args:
            joke (str): The joke to add
        
        Raises:
            TypeError: If the joke is not a string
            ValueError: If the joke is empty
        """
        if not isinstance(joke, str):
            raise TypeError("Joke must be a string")
        
        joke = joke.strip()
        if not joke:
            raise ValueError("Joke cannot be empty")
        
        if joke not in self.jokes:
            self.jokes.append(joke)
        
        return len(self.jokes)

    def get_joke_count(self):
        """
        Returns the number of jokes in the collection.
        
        Returns:
            int: The number of jokes
        """
        return len(self.jokes)