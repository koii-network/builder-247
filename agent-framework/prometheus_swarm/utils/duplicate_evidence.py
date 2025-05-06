import logging
from typing import List, Dict, Any, Optional

class DuplicateEvidenceError(Exception):
    """Custom exception for duplicate evidence scenarios."""
    pass

def validate_unique_evidence(evidence_list: List[Dict[Any, Any]], 
                              unique_key: str = 'id') -> None:
    """
    Validate that evidence entries are unique based on a specified key.

    Args:
        evidence_list (List[Dict[Any, Any]]): List of evidence dictionaries
        unique_key (str, optional): Key used to determine uniqueness. Defaults to 'id'.

    Raises:
        DuplicateEvidenceError: If duplicate evidence is detected
    """
    logger = logging.getLogger(__name__)
    
    # Check for duplicates
    seen_keys = set()
    duplicates = []

    for item in evidence_list:
        if unique_key not in item:
            logger.warning(f"Evidence item missing unique key '{unique_key}': {item}")
            continue

        current_key = item[unique_key]
        
        if current_key in seen_keys:
            duplicates.append(current_key)
            logger.error(f"Duplicate evidence found with {unique_key}: {current_key}")
        
        seen_keys.add(current_key)

    if duplicates:
        raise DuplicateEvidenceError(
            f"Duplicate evidence detected for {unique_key}s: {duplicates}"
        )

def log_evidence_summary(evidence_list: List[Dict[Any, Any]], 
                          log_level: str = 'INFO') -> None:
    """
    Log a summary of evidence entries with configurable log level.

    Args:
        evidence_list (List[Dict[Any, Any]]): List of evidence dictionaries
        log_level (str, optional): Logging level. Defaults to 'INFO'.
    """
    logger = logging.getLogger(__name__)
    log_method = getattr(logger, log_level.lower(), logger.info)

    log_method(f"Total evidence entries: {len(evidence_list)}")
    log_method(f"Evidence keys: {list(evidence_list[0].keys()) if evidence_list else 'N/A'}")

def filter_duplicates(evidence_list: List[Dict[Any, Any]], 
                      unique_key: str = 'id', 
                      keep: str = 'first') -> List[Dict[Any, Any]]:
    """
    Filter out duplicate evidence entries while preserving desired entries.

    Args:
        evidence_list (List[Dict[Any, Any]]): List of evidence dictionaries
        unique_key (str, optional): Key used to determine uniqueness. Defaults to 'id'.
        keep (str, optional): Strategy for keeping duplicates. 
                               'first' keeps first occurrence, 'last' keeps last. 
                               Defaults to 'first'.

    Returns:
        List[Dict[Any, Any]]: Filtered list of evidence without duplicates
    """
    logger = logging.getLogger(__name__)
    
    if keep not in ['first', 'last']:
        raise ValueError("'keep' must be either 'first' or 'last'")

    seen_keys = set()
    filtered_evidence = []

    if keep == 'first':
        for item in evidence_list:
            if unique_key not in item:
                logger.warning(f"Evidence item missing unique key '{unique_key}': {item}")
                continue

            current_key = item[unique_key]
            
            if current_key not in seen_keys:
                filtered_evidence.append(item)
                seen_keys.add(current_key)
    
    else:  # keep == 'last'
        for item in reversed(evidence_list):
            if unique_key not in item:
                logger.warning(f"Evidence item missing unique key '{unique_key}': {item}")
                continue

            current_key = item[unique_key]
            
            if current_key not in seen_keys:
                filtered_evidence.insert(0, item)
                seen_keys.add(current_key)

    return filtered_evidence