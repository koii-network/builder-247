import logging
from typing import Any, Dict, List

class DuplicateEvidenceError(Exception):
    """Custom exception for handling duplicate evidence scenarios."""
    def __init__(self, message: str, existing_evidence: List[Dict[str, Any]] = None):
        """
        Initialize DuplicateEvidenceError with detailed information.
        
        Args:
            message (str): Description of the duplicate evidence error
            existing_evidence (List[Dict[str, Any]], optional): List of existing evidence entries
        """
        self.message = message
        self.existing_evidence = existing_evidence or []
        super().__init__(self.message)

def log_duplicate_evidence(evidence: Dict[str, Any], existing_entries: List[Dict[str, Any]]) -> None:
    """
    Log details about duplicate evidence.
    
    Args:
        evidence (Dict[str, Any]): The evidence being checked
        existing_entries (List[Dict[str, Any]]): List of existing evidence entries
    """
    logger = logging.getLogger(__name__)
    logger.warning(
        "Duplicate evidence detected",
        extra={
            "current_evidence": evidence,
            "existing_entries_count": len(existing_entries),
            "existing_entries_ids": [entry.get('id') for entry in existing_entries]
        }
    )

def check_duplicate_evidence(new_evidence: Dict[str, Any], existing_evidence: List[Dict[str, Any]], unique_key: str = 'id') -> None:
    """
    Check for duplicate evidence and raise an error if duplicates are found.
    
    Args:
        new_evidence (Dict[str, Any]): The new evidence to be added
        existing_evidence (List[Dict[str, Any]]): List of existing evidence
        unique_key (str, optional): Key to use for identifying duplicates. Defaults to 'id'.
    
    Raises:
        DuplicateEvidenceError: If duplicate evidence is found
    """
    duplicates = [
        entry for entry in existing_evidence 
        if entry.get(unique_key) == new_evidence.get(unique_key)
    ]
    
    if duplicates:
        log_duplicate_evidence(new_evidence, duplicates)
        raise DuplicateEvidenceError(
            f"Evidence with {unique_key} '{new_evidence.get(unique_key)}' already exists",
            existing_evidence=duplicates
        )