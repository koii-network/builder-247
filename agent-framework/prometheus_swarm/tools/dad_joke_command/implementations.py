import random

def get_random_dad_joke():
    """
    Generate a random dad joke.

    Returns:
        str: A humorous dad joke
    """
    dad_jokes = [
        "I'm afraid for the calendar. Its days are numbered.",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why don't scientists trust atoms? Because they make up everything!",
        "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing!",
        "I told my son I was named after Thomas Edison... He said, 'But dad, your name is John.' I said, 'I know, I was named AFTER him.'",
        "Why do bees have sticky hair? Because they use honeycombs.",
        "I don't trust stairs. They're always up to something.",
        "What do you call a fake noodle? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "I used to be addicted to soap, but I'm clean now."
    ]
    return random.choice(dad_jokes)

def dad_joke_command_handler():
    """
    Command handler for generating a random dad joke.

    Returns:
        dict: A dictionary containing the dad joke
    """
    joke = get_random_dad_joke()
    return {
        "type": "text",
        "text": joke
    }