import logging
from typing import Any, List, Dict, Optional

logger = logging.getLogger(__name__)

class DuplicateEvidenceError(Exception):
    """Custom exception for handling duplicate evidence scenarios."""
    pass

def detect_duplicate_evidence(evidence_list: List[Dict[str, Any]], 
                               unique_keys: Optional[List[str]] = None,
                               allow_duplicates: bool = False) -> List[Dict[str, Any]]:
    """
    Detect and handle duplicate evidence in a list of evidence items.

    Args:
        evidence_list (List[Dict[str, Any]]): List of evidence items to check
        unique_keys (Optional[List[str]], optional): Keys to use for uniqueness check. 
                                                     Defaults to checking all keys.
        allow_duplicates (bool, optional): If True, do not raise error on duplicates. Defaults to False.

    Returns:
        List[Dict[str, Any]]: List of unique evidence items

    Raises:
        DuplicateEvidenceError: If duplicates are found and cannot be resolved
    """
    if not evidence_list:
        logger.info("Empty evidence list provided")
        return []

    # If no unique keys specified, use all keys
    if unique_keys is None:
        unique_keys = list(evidence_list[0].keys())

    # Track unique evidence and duplicates
    unique_evidence = []
    duplicate_evidence = []

    for evidence in evidence_list:
        # Check if current evidence is a duplicate
        is_duplicate = any(
            all(evidence.get(key) == existing.get(key) for key in unique_keys)
            for existing in unique_evidence
        )

        if is_duplicate:
            duplicate_evidence.append(evidence)
            logger.warning(f"Duplicate evidence detected: {evidence}")
        else:
            unique_evidence.append(evidence)

    # Log duplicate summary
    if duplicate_evidence:
        logger.info(f"Found {len(duplicate_evidence)} duplicate evidence items")
        
        # Optional: Raise an error if duplicates are critical
        if not allow_duplicates and len(duplicate_evidence) > 0:
            raise DuplicateEvidenceError(f"Found {len(duplicate_evidence)} duplicate evidence items")

    return unique_evidence if not allow_duplicates else evidence_list

def log_duplicate_evidence(evidence_list: List[Dict[str, Any]], 
                            log_level: int = logging.WARNING,
                            unique_keys: Optional[List[str]] = None) -> None:
    """
    Log information about duplicate evidence without removing them.

    Args:
        evidence_list (List[Dict[str, Any]]): List of evidence items to log
        log_level (int, optional): Logging level. Defaults to logging.WARNING.
        unique_keys (Optional[List[str]], optional): Keys to use for duplicate detection.
    """
    if not unique_keys:
        # Use all keys if not specified
        unique_keys = list(evidence_list[0].keys()) if evidence_list else []

    # Track unique and duplicate evidence
    unique_evidence = set()
    duplicates = []

    for evidence in evidence_list:
        # Create a tuple of values for keys used to identify uniqueness
        unique_tuple = tuple(str(evidence.get(key, '')) for key in unique_keys)
        
        if unique_tuple in unique_evidence:
            duplicates.append(evidence)
        else:
            unique_evidence.add(unique_tuple)

    # Log duplicate details
    if duplicates:
        logger.log(log_level, f"Total duplicate evidence found: {len(duplicates)}")
        for dup in duplicates:
            logger.log(log_level, f"Duplicate Evidence: {dup}")