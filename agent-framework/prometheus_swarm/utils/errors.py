"""Custom exceptions for Prometheus Swarm framework."""

class DuplicateEvidenceError(Exception):
    """Exception raised when duplicate evidence is detected.
    
    Attributes:
        message (str): Explanation of the error
        evidence_id (str, optional): Identifier of the duplicate evidence
    """
    
    def __init__(self, message: str, evidence_id: str = None):
        """
        Initialize the DuplicateEvidenceError.
        
        Args:
            message (str): Detailed error message
            evidence_id (str, optional): Identifier of the duplicate evidence
        """
        self.message = message
        self.evidence_id = evidence_id
        super().__init__(self.message)
    
    def __str__(self):
        """
        String representation of the error.
        
        Returns:
            str: Formatted error message with optional evidence ID
        """
        if self.evidence_id:
            return f"{self.message} (Evidence ID: {self.evidence_id})"
        return self.message