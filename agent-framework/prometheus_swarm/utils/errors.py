class CustomError(Exception):
    """
    A custom error class that provides enhanced error handling capabilities.
    
    Attributes:
        message (str): The error message
        context (dict): Additional context about the error
    """
    def __init__(self, message="", context=None):
        """
        Initialize a CustomError.
        
        Args:
            message (str, optional): Descriptive error message. Defaults to "".
            context (dict, optional): Additional error context. Defaults to None.
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self):
        """
        String representation of the error.
        
        Returns:
            str: The error message
        """
        return self.message

    def __repr__(self):
        """
        Detailed representation of the error.
        
        Returns:
            str: A detailed string representation
        """
        if self.context:
            return f"CustomError(message='{self.message}', context={self.context})"
        return f"CustomError(message='{self.message}')"

    def add_context(self, key, value):
        """
        Add additional context to the error.
        
        Args:
            key (str): Context key
            value (Any): Context value
        """
        self.context[key] = value