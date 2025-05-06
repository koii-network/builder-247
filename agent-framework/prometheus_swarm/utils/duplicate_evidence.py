import logging
from typing import Any, List, Dict

class DuplicateEvidenceError(Exception):
    """Custom exception for duplicate evidence scenarios."""
    pass

def check_duplicate_evidence(evidence_list: List[Dict[str, Any]], 
                              unique_key: str = 'id') -> List[Dict[str, Any]]:
    """
    Check for duplicate evidence based on a unique key.

    Args:
        evidence_list (List[Dict[str, Any]]): List of evidence dictionaries
        unique_key (str, optional): Key to use for identifying duplicates. Defaults to 'id'.

    Returns:
        List[Dict[str, Any]]: List of unique evidence entries

    Raises:
        DuplicateEvidenceError: If duplicate evidence is detected and cannot be resolved
    """
    # Configure logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Check if logging handler exists, if not add a stream handler
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Track unique and duplicate evidence
    unique_evidence = []
    duplicate_evidence = []
    seen_keys = set()

    for evidence in evidence_list:
        # Check if the unique key exists
        if unique_key not in evidence:
            logger.warning(f"Evidence missing unique key '{unique_key}': {evidence}")
            unique_evidence.append(evidence)
            continue

        unique_value = evidence[unique_key]

        # Check for duplicates
        if unique_value in seen_keys:
            duplicate_evidence.append(evidence)
            logger.warning(f"Duplicate evidence detected: {evidence}")
        else:
            seen_keys.add(unique_value)
            unique_evidence.append(evidence)

    # If duplicates are found, raise an error or log a warning based on severity
    if duplicate_evidence:
        logger.error(f"Found {len(duplicate_evidence)} duplicate evidence entries")
        raise DuplicateEvidenceError(f"Duplicate evidence detected: {duplicate_evidence}")

    return unique_evidence

def log_duplicate_evidence(duplicate_entries: List[Dict[str, Any]], 
                            log_level: int = logging.WARNING) -> None:
    """
    Log duplicate evidence entries with specified log level.

    Args:
        duplicate_entries (List[Dict[str, Any]]): List of duplicate evidence entries
        log_level (int, optional): Logging level. Defaults to logging.WARNING.
    """
    logger = logging.getLogger(__name__)
    
    for entry in duplicate_entries:
        logger.log(log_level, f"Duplicate Evidence: {entry}")