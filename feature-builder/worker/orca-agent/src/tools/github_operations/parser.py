"""Module for parsing GitHub PR descriptions."""

import re
from typing import Dict, List, Union, Optional


def extract_section(content: str, section: str) -> Optional[str]:
    """Extract a section from content using markers.

    Args:
        content: The content to parse
        section: The section name (e.g., 'TODO', 'DESCRIPTION')

    Returns:
        The content between the markers, or None if not found
    """
    pattern = f"<!-- BEGIN_{section} -->\\s*(.+?)\\s*<!-- END_{section} -->"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else None


def parse_list_content(content: str) -> List[str]:
    """Parse content that should be a list (like acceptance criteria or tests).

    Args:
        content: The content to parse into a list

    Returns:
        List of items, stripped of markers and whitespace
    """
    if not content:
        return []
    # Split on newlines and process each line
    items = []
    for line in content.split("\n"):
        # Remove list markers and whitespace
        item = line.strip("- *").strip()
        if item:
            items.append(item)
    return items


def parse_pr_description(description: str) -> Dict[str, Union[str, List[str]]]:
    """Parse a PR description created with our template.

    Args:
        description: The PR description to parse

    Returns:
        Dictionary containing:
            - todo: Original task description
            - title: PR title
            - description: Changes description
            - acceptance_criteria: List of acceptance criteria
            - tests: List of tests
    """
    # Extract each section
    sections = {
        "todo": extract_section(description, "TODO"),
        "title": extract_section(description, "TITLE"),
        "description": extract_section(description, "DESCRIPTION"),
        "acceptance_criteria": extract_section(description, "ACCEPTANCE_CRITERIA"),
        "tests": extract_section(description, "TESTS"),
    }

    # Parse lists for acceptance criteria and tests
    if sections["acceptance_criteria"]:
        sections["acceptance_criteria"] = parse_list_content(
            sections["acceptance_criteria"]
        )
    if sections["tests"]:
        sections["tests"] = parse_list_content(sections["tests"])

    return sections


def validate_pr_content(pr_info: Dict[str, Union[str, List[str]]]) -> List[str]:
    """Validate that all required sections are present and non-empty.

    Args:
        pr_info: The parsed PR information

    Returns:
        List of validation errors, empty if all valid
    """
    errors = []

    # Required sections
    required = {
        "todo": "Task description",
        "title": "PR title",
        "description": "Changes description",
        "acceptance_criteria": "Acceptance criteria",
        "tests": "Tests",
    }

    for key, name in required.items():
        if key not in pr_info or not pr_info[key]:
            errors.append(f"Missing {name}")
        elif isinstance(pr_info[key], list) and not pr_info[key]:
            errors.append(f"Empty {name}")

    return errors
