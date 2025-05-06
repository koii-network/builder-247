import logging
from typing import Any, Dict

class DuplicateEvidenceError(Exception):
    """
    Custom exception raised when duplicate evidence is detected.
    
    Attributes:
        message (str): Description of the duplicate evidence error
        evidence (Dict[str, Any]): The duplicate evidence details
    """
    def __init__(self, message: str, evidence: Dict[str, Any]):
        self.message = message
        self.evidence = evidence
        super().__init__(self.message)

def log_duplicate_evidence(evidence: Dict[str, Any]) -> None:
    """
    Log details of duplicate evidence with appropriate logging level.
    
    Args:
        evidence (Dict[str, Any]): Details of the duplicate evidence
    """
    logger = logging.getLogger('duplicate_evidence')
    logger.warning(
        f"Duplicate evidence detected: {evidence}",
        extra={
            'evidence': evidence
        }
    )