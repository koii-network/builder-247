from typing import Dict, Any, Optional

class Evidence:
    """
    Represents a piece of evidence with unique identification.
    
    Attributes:
        identifier (str): A unique identifier for the evidence.
        content (str): The main content or description of the evidence.
        source (str): The origin or source of the evidence.
        additional_metadata (Dict[str, Any], optional): Additional metadata associated with the evidence.
    """

    def __init__(
        self,
        identifier: str,
        content: str,
        source: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an Evidence instance.
        
        Args:
            identifier (str): A unique identifier for the evidence.
            content (str): The main content or description of the evidence.
            source (str): The origin or source of the evidence.
            additional_metadata (Dict[str, Any], optional): Additional metadata for the evidence.
        """
        self.identifier = identifier
        self.content = content
        self.source = source
        self.additional_metadata = additional_metadata or {}