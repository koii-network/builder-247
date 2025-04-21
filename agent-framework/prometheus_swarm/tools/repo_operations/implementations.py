"""Repository operations tool implementations."""

from typing import Dict, Any
from prometheus_swarm.utils.logging import log_key_value
from prometheus_swarm.tools.repo_operations.Types import RepoType, Language, TestFramework


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
        "data": {"repo_type": repo_type},
    }

def classify_language(language: str, **kwargs) -> Dict[str, Any]: 
    """
    Get a README prompt customized for a specific language.

    Args:
        language: The language (must be one of the Language enum values)

    Returns:
        A dictionary with the tool execution result containing the formatted prompt
    """
    # Validate that language is one of the enum values
    valid_languages = [l.value for l in Language]
    if language not in valid_languages:
        return {
            "success": False,
            "message": f"Invalid language: {language}. Must be one of: {', '.join(valid_languages)}",
            "data": {
                "language": language,
            },
        }
    return {
        "success": True,
        "message": f"Fetched README prompt for language: {language}",
        "data": {"language": language},
    }

def classify_test_framework(test_framework: str, **kwargs) -> Dict[str, Any]:
    """
    Get a README prompt customized for a specific test framework.

    Args:
        test_framework: The test framework (must be one of the TestFramework enum values)

    Returns:
        A dictionary with the tool execution result containing the formatted prompt
    """
    # Validate that test_framework is one of the enum values
    valid_test_frameworks = [t.value for t in TestFramework]
    if test_framework not in valid_test_frameworks:
        return {
            "success": False,
            "message": f"Invalid test framework: {test_framework}. Must be one of: {', '.join(valid_test_frameworks)}",
            "data": {
                "test_framework": test_framework,
            },
        }
    return {
        "success": True,
        "message": f"Fetched README prompt for test framework: {test_framework}",
        "data": {"test_framework": test_framework},
    }
