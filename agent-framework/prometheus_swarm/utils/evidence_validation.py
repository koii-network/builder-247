"""
Module for server-side evidence uniqueness validation.

This module provides functionality to validate the uniqueness of evidence 
in a distributed computing environment.
"""

from typing import Any, Dict, List, Optional
import hashlib
import json


class EvidenceValidationError(Exception):
    """Exception raised for evidence validation errors."""
    pass


def generate_evidence_hash(evidence: Dict[str, Any]) -> str:
    """
    Generate a unique hash for the given evidence.

    Args:
        evidence (Dict[str, Any]): The evidence dictionary to hash.

    Returns:
        str: A deterministic hash representing the evidence.

    Raises:
        EvidenceValidationError: If the evidence cannot be serialized.
    """
    try:
        # Sort the dictionary to ensure consistent hashing
        sorted_evidence = json.dumps(evidence, sort_keys=True)
        return hashlib.sha256(sorted_evidence.encode()).hexdigest()
    except (TypeError, ValueError) as e:
        raise EvidenceValidationError(f"Cannot generate hash for evidence: {e}")


def validate_evidence_uniqueness(
    evidence: Dict[str, Any], 
    existing_evidences: List[Dict[str, Any]]
) -> bool:
    """
    Validate the uniqueness of evidence against existing evidences.

    Args:
        evidence (Dict[str, Any]): The evidence to validate.
        existing_evidences (List[Dict[str, Any]]): List of existing evidences.

    Returns:
        bool: True if the evidence is unique, False otherwise.

    Raises:
        EvidenceValidationError: If evidence validation fails.
    """
    if not isinstance(evidence, dict):
        raise EvidenceValidationError("Evidence must be a dictionary")

    if not isinstance(existing_evidences, list):
        raise EvidenceValidationError("Existing evidences must be a list")

    try:
        new_evidence_hash = generate_evidence_hash(evidence)
        
        # Check uniqueness by comparing hashes
        existing_hashes = [
            generate_evidence_hash(existing_ev) 
            for existing_ev in existing_evidences
        ]

        return new_evidence_hash not in existing_hashes
    except EvidenceValidationError as e:
        raise EvidenceValidationError(f"Uniqueness validation failed: {e}")


def filter_unique_evidences(
    new_evidences: List[Dict[str, Any]], 
    existing_evidences: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filter out non-unique evidences from a list of new evidences.

    Args:
        new_evidences (List[Dict[str, Any]]): List of new evidences to filter.
        existing_evidences (List[Dict[str, Any]]): List of existing evidences.

    Returns:
        List[Dict[str, Any]]: List of unique evidences.

    Raises:
        EvidenceValidationError: If evidence validation fails.
    """
    if not isinstance(new_evidences, list):
        raise EvidenceValidationError("New evidences must be a list")

    unique_evidences = []
    for evidence in new_evidences:
        try:
            if validate_evidence_uniqueness(evidence, existing_evidences + unique_evidences):
                unique_evidences.append(evidence)
        except EvidenceValidationError:
            # Optionally log the validation error
            continue

    return unique_evidences