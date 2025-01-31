"""Module for handling PR template validation."""

import re
from typing import Dict, Any


def validate_pr_description(description: str) -> Dict[str, Any]:
    """
    Validate that a PR description matches the required template format.

    Args:
        description (str): The PR description to validate

    Returns:
        Dict[str, Any]: A dictionary containing:
            - valid (bool): Whether the description is valid
            - errors (list): List of validation errors if invalid
    """
    required_sections = [
        "Type of Change",
        "Description",
        "Related Issues",
        "Testing Done",
        "Checklist",
    ]

    errors = []

    # Check for required sections
    for section in required_sections:
        if f"## {section}" not in description:
            errors.append(f"Missing required section: {section}")

    # Check Type of Change selections
    type_pattern = (
        r"\[x\] (?:Bug fix|New feature|Documentation update|Code refactoring|Other)"
    )
    if "## Type of Change" in description:
        type_section = description.split("## Type of Change")[1].split("##")[0]
        if not re.search(type_pattern, type_section, re.IGNORECASE):
            errors.append("Must select at least one Type of Change")

    # Check Description content
    if "## Description" in description:
        desc_section = description.split("## Description")[1].split("##")[0].strip()
        if (
            not desc_section or len(desc_section.split()) < 10
        ):  # Require at least 10 words
            errors.append("Description section is too short (minimum 10 words)")

    # Check Testing Done content
    if "## Testing Done" in description:
        test_section = description.split("## Testing Done")[1].split("##")[0].strip()
        if (
            not test_section or len(test_section.split()) < 5
        ):  # Require at least 5 words
            errors.append("Testing Done section is too short (minimum 5 words)")

    # Check Checklist selections
    checklist_pattern = r"\[x\] I have tested my changes"
    if "## Checklist" in description:
        checklist_section = description.split("## Checklist")[1].strip()
        if not re.search(checklist_pattern, checklist_section, re.IGNORECASE):
            errors.append("Must confirm testing in the checklist")

    return {"valid": len(errors) == 0, "errors": errors}
