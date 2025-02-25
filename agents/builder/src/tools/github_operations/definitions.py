from src.tools.github_operations.implementations import (
    fork_repository,
    create_pull_request,
    review_pull_request,
    validate_implementation,
)

DEFINITIONS = {
    "fork_repository": {
        "name": "fork_repository",
        "description": "Fork a repository and optionally clone it locally.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_full_name": {
                    "type": "string",
                    "description": "Full name of repository (owner/repo)",
                },
                "repo_path": {
                    "type": "string",
                    "description": "Local path to clone to",
                },
            },
            "required": ["repo_full_name"],
        },
        "function": fork_repository,
    },
    "create_pull_request": {
        "name": "create_pull_request",
        "description": "Create a pull request with formatted description.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_full_name": {
                    "type": "string",
                    "description": "Full name of repository (owner/repo)",
                },
                "title": {"type": "string", "description": "Title of the pull request"},
                "head": {
                    "type": "string",
                    "description": "Name of the branch containing changes",
                },
                "base": {
                    "type": "string",
                    "description": "Name of the branch to merge into",
                },
                "summary": {"type": "string", "description": "Summary of changes"},
                "tests": {"type": "string", "description": "Description of tests"},
                "todo": {"type": "string", "description": "Original task description"},
                "acceptance_criteria": {
                    "type": "string",
                    "description": "Acceptance criteria",
                },
            },
            "required": [
                "repo_full_name",
                "title",
                "head",
                "summary",
                "tests",
                "todo",
                "acceptance_criteria",
            ],
        },
        "return_value": True,
        "function": create_pull_request,
    },
    "review_pull_request": {
        "name": "review_pull_request",
        "description": "Review a pull request and post a structured review comment.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_full_name": {
                    "type": "string",
                    "description": "Full name of repository (owner/repo)",
                },
                "pr_number": {"type": "integer", "description": "Pull request number"},
                "title": {"type": "string", "description": "Title of the PR"},
                "summary": {"type": "string", "description": "Summary of changes"},
                "requirements": {
                    "type": "object",
                    "description": "Dictionary with 'met' and 'not_met' requirements",
                    "properties": {
                        "met": {"type": "array", "items": {"type": "string"}},
                        "not_met": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "test_evaluation": {
                    "type": "object",
                    "description": "Dictionary with test evaluation details",
                    "properties": {
                        "coverage": {"type": "array", "items": {"type": "string"}},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "missing": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "recommendation": {
                    "type": "string",
                    "description": "APPROVE/REVISE/REJECT",
                },
                "recommendation_reason": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Reasons for recommendation",
                },
                "action_items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Required changes or improvements",
                },
            },
            "required": [
                "repo_full_name",
                "pr_number",
                "title",
                "summary",
                "requirements",
                "test_evaluation",
                "recommendation",
                "recommendation_reason",
                "action_items",
            ],
        },
        "return_value": True,
        "function": review_pull_request,
    },
    "validate_implementation": {
        "name": "validate_implementation",
        "description": "Validate that an implementation meets its requirements.",
        "parameters": {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the validation passed",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for failure if validation failed",
                },
            },
            "required": ["success"],
        },
        "return_value": True,
        "function": validate_implementation,
    },
}
