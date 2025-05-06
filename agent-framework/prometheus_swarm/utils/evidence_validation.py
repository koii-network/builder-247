"""
Module for server-side evidence uniqueness validation.

This module provides functions to validate the uniqueness of evidence in task submissions.
"""

from typing import Dict, Any, List


class EvidenceValidationError(Exception):
    """Custom exception for evidence validation failures."""
    pass


def validate_evidence_uniqueness(submissions: List[Dict[str, Any]], new_submission: Dict[str, Any]) -> bool:
    """
    Validate the uniqueness of evidence across multiple submissions.

    Args:
        submissions (List[Dict[str, Any]]): Existing submissions to check against
        new_submission (Dict[str, Any]): New submission to validate

    Returns:
        bool: True if the evidence is unique, False otherwise

    Raises:
        EvidenceValidationError: If evidence validation fails
    """
    # Check if evidence is present in the new submission
    if 'evidence' not in new_submission:
        raise EvidenceValidationError("No evidence provided in submission")

    new_evidence = new_submission['evidence']

    # Perform uniqueness check across existing submissions
    for existing_submission in submissions:
        if 'evidence' in existing_submission:
            # Compare hash or unique identifier of evidence
            if _are_evidences_similar(existing_submission['evidence'], new_evidence):
                raise EvidenceValidationError("Evidence is not unique")

    return True


def _are_evidences_similar(evidence1: Any, evidence2: Any, similarity_threshold: float = 0.9) -> bool:
    """
    Compare two pieces of evidence for similarity.

    Args:
        evidence1 (Any): First piece of evidence
        evidence2 (Any): Second piece of evidence
        similarity_threshold (float): Threshold for considering evidences similar

    Returns:
        bool: True if evidences are similar, False otherwise
    """
    # If evidence is a string, use string comparison
    if isinstance(evidence1, str) and isinstance(evidence2, str):
        # Simple string comparison
        return evidence1.strip().lower() == evidence2.strip().lower()

    # If evidence is a dict or more complex structure, implement advanced comparison
    if isinstance(evidence1, dict) and isinstance(evidence2, dict):
        # Compare keys and values
        shared_keys = set(evidence1.keys()) & set(evidence2.keys())
        matching_count = sum(1 for key in shared_keys if evidence1[key] == evidence2[key])
        similarity_ratio = matching_count / len(shared_keys) if shared_keys else 0

        return similarity_ratio >= similarity_threshold

    # For other types, use simple equality
    return evidence1 == evidence2