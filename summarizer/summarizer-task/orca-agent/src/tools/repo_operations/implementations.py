"""Repository operations tool implementations."""

from typing import Dict, Any
from src.utils.logging import log_key_value
from src.workflows.repoSummarizer.phases import RepoType


def classify_repository(repo_type: str, **kwargs) -> Dict[str, Any]:
    """
    Get a README prompt customized for a specific repository type.

    Args:
        repo_type: The repository type (must be one of the RepoType enum values)

    Returns:
        A dictionary with the tool execution result containing the formatted prompt
    """
    # Validate that repo_type is one of the enum values
    valid_types = [t.value for t in RepoType]
    if repo_type not in valid_types:
        return {
            "success": False,
            "message": f"Invalid repository type: {repo_type}. Must be one of: {', '.join(valid_types)}",
            "data": None,
        }

    # Log which template is being used
    log_key_value("Using README template for", repo_type)

    return {
        "success": True,
        "message": f"Fetched README prompt for repository type: {repo_type}",
        "data": {"prompt_name": repo_type},
    }
