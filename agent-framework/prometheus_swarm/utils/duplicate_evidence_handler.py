import logging
from typing import Any, Dict, List

class DuplicateEvidenceError(Exception):
    """Custom exception for handling duplicate evidence scenarios."""
    pass

class DuplicateEvidenceHandler:
    """
    A utility class to handle and log duplicate evidence with configurable logging.
    
    This class provides methods to:
    - Check for duplicate evidence
    - Log duplicate evidence occurrences
    - Optionally raise exceptions for duplicates
    """
    
    def __init__(self, logger: logging.Logger = None, raise_on_duplicate: bool = False):
        """
        Initialize the DuplicateEvidenceHandler.
        
        Args:
            logger (logging.Logger, optional): Custom logger. If not provided, 
                                               creates a default logger.
            raise_on_duplicate (bool, optional): Whether to raise an exception 
                                                 on duplicate evidence. Defaults to False.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.raise_on_duplicate = raise_on_duplicate
        
    def check_duplicates(self, evidence_list: List[Dict[str, Any]], 
                          identifier_key: str = 'id') -> List[Dict[str, Any]]:
        """
        Check for duplicate evidence in the given list.
        
        Args:
            evidence_list (List[Dict[str, Any]]): List of evidence dictionaries
            identifier_key (str, optional): Key to use for identifying unique evidence. 
                                            Defaults to 'id'.
        
        Returns:
            List[Dict[str, Any]]: List of duplicate evidence entries
        
        Raises:
            DuplicateEvidenceError: If raise_on_duplicate is True and duplicates are found
        """
        # Track seen identifiers and duplicates
        seen_identifiers = set()
        duplicates = []
        
        for evidence in evidence_list:
            identifier = evidence.get(identifier_key)
            
            if identifier is None:
                self.logger.warning(f"Evidence missing identifier key '{identifier_key}': {evidence}")
                continue
            
            if identifier in seen_identifiers:
                # Log the duplicate
                self.logger.warning(f"Duplicate evidence found: {evidence}")
                duplicates.append(evidence)
                
                # Optionally raise an exception
                if self.raise_on_duplicate:
                    raise DuplicateEvidenceError(f"Duplicate evidence with {identifier_key}='{identifier}'")
            else:
                seen_identifiers.add(identifier)
        
        return duplicates
    
    def remove_duplicates(self, evidence_list: List[Dict[str, Any]], 
                           identifier_key: str = 'id') -> List[Dict[str, Any]]:
        """
        Remove duplicate evidence from the list, keeping first occurrence.
        
        Args:
            evidence_list (List[Dict[str, Any]]): List of evidence dictionaries
            identifier_key (str, optional): Key to use for identifying unique evidence. 
                                            Defaults to 'id'.
        
        Returns:
            List[Dict[str, Any]]: List of evidence without duplicates
        """
        seen_identifiers = set()
        unique_evidence = []
        
        for evidence in evidence_list:
            identifier = evidence.get(identifier_key)
            
            if identifier is None:
                self.logger.warning(f"Evidence missing identifier key '{identifier_key}': {evidence}")
                unique_evidence.append(evidence)
                continue
            
            if identifier not in seen_identifiers:
                unique_evidence.append(evidence)
                seen_identifiers.add(identifier)
            else:
                self.logger.info(f"Removing duplicate evidence: {evidence}")
        
        return unique_evidence