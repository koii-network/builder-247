import logging
from typing import List, Dict, Any, Optional

class DuplicateEvidenceError(Exception):
    """Custom exception for duplicate evidence detection."""
    pass

def detect_duplicate_evidence(evidence_list: List[Dict[str, Any]], 
                               identifier_key: str = 'id', 
                               logger: Optional[logging.Logger] = None) -> List[Dict[str, Any]]:
    """
    Detect and handle duplicate evidence in a list of evidence dictionaries.

    Args:
        evidence_list (List[Dict[str, Any]]): List of evidence dictionaries
        identifier_key (str, optional): Key used to identify unique evidence. Defaults to 'id'.
        logger (Optional[logging.Logger], optional): Logger for recording duplicate evidence. 
                                                    If not provided, will use root logger.

    Returns:
        List[Dict[str, Any]]: List of unique evidence

    Raises:
        DuplicateEvidenceError: If duplicate evidence is detected and cannot be resolved
    """
    if not logger:
        logger = logging.getLogger(__name__)

    # Track unique evidence and duplicate entries
    unique_evidence = []
    duplicate_evidence = []

    # Track seen identifiers to detect duplicates
    seen_identifiers = set()

    for evidence in evidence_list:
        identifier = evidence.get(identifier_key)

        if identifier is None:
            logger.warning(f"Evidence missing identifier key '{identifier_key}': {evidence}")
            unique_evidence.append(evidence)
            continue

        if identifier in seen_identifiers:
            duplicate_evidence.append(evidence)
            logger.warning(f"Duplicate evidence detected for {identifier_key}: {identifier}")
        else:
            seen_identifiers.add(identifier)
            unique_evidence.append(evidence)

    if duplicate_evidence:
        # Log total number of duplicates
        logger.error(f"Total duplicate evidence: {len(duplicate_evidence)}")
        
        # Optional: Configure behavior for handling duplicates
        # Current implementation keeps first occurrence and logs others
        if len(duplicate_evidence) > 0:
            raise DuplicateEvidenceError(f"Found {len(duplicate_evidence)} duplicate evidence entries")

    return unique_evidence