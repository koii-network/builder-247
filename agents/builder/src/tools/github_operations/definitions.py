from src.tools.github_operations.implementations import (
    fork_repository,
    create_worker_pull_request,
    create_leader_pull_request,
    review_pull_request,
    validate_implementation,
    generate_analysis,
    merge_pull_request,
    generate_tasks,
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
    "create_worker_pull_request": {
        "name": "create_worker_pull_request",
        "description": "Create a pull request for a worker node with task implementation details and signatures.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_owner": {
                    "type": "string",
                    "description": "Owner of the repository",
                },
                "repo_name": {
                    "type": "string",
                    "description": "Name of the repository",
                },
                "title": {
                    "type": "string",
                    "description": "Title of the pull request",
                },
                "head_branch": {
                    "type": "string",
                    "description": "Name of the branch containing changes",
                },
                "description": {
                    "type": "string",
                    "description": "Brief 1-2 sentence overview of the work done",
                },
                "changes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Detailed list of specific changes made in the implementation",
                },
                "tests": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of test descriptions",
                },
                "todo": {
                    "type": "string",
                    "description": "Original task description",
                },
                "acceptance_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of acceptance criteria",
                },
                "staking_key": {
                    "type": "string",
                    "description": "Worker's staking key",
                },
                "pub_key": {
                    "type": "string",
                    "description": "Worker's public key",
                },
                "staking_signature": {
                    "type": "string",
                    "description": "Worker's staking signature",
                },
                "public_signature": {
                    "type": "string",
                    "description": "Worker's public signature",
                },
            },
            "required": [
                "repo_owner",
                "repo_name",
                "title",
                "head_branch",
                "description",
                "changes",
                "tests",
                "todo",
                "acceptance_criteria",
                "staking_key",
                "pub_key",
                "staking_signature",
                "public_signature",
            ],
        },
        "function": create_worker_pull_request,
    },
    "create_leader_pull_request": {
        "name": "create_leader_pull_request",
        "description": "Create a pull request for a leader node consolidating multiple worker PRs.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_owner": {
                    "type": "string",
                    "description": "Owner of the repository",
                },
                "repo_name": {
                    "type": "string",
                    "description": "Name of the repository",
                },
                "title": {
                    "type": "string",
                    "description": "Title of the pull request",
                },
                "head_branch": {
                    "type": "string",
                    "description": "Name of the branch containing changes",
                },
                "description": {
                    "type": "array",
                    "description": "List of consolidated PRs, each containing number, url, and title",
                    "items": {
                        "type": "object",
                        "properties": {
                            "number": {"type": "integer"},
                            "url": {"type": "string"},
                            "title": {"type": "string"},
                        },
                    },
                },
                "base_branch": {
                    "type": "string",
                    "description": "Base branch to merge into (default: main)",
                    "default": "main",
                },
                "staking_key": {
                    "type": "string",
                    "description": "Leader's staking key",
                },
                "pub_key": {
                    "type": "string",
                    "description": "Leader's public key",
                },
                "staking_signature": {
                    "type": "string",
                    "description": "Leader's staking signature",
                },
                "public_signature": {
                    "type": "string",
                    "description": "Leader's public signature",
                },
            },
            "required": [
                "repo_owner",
                "repo_name",
                "title",
                "head_branch",
                "description",
            ],
        },
        "function": create_leader_pull_request,
    },
    "review_pull_request": {
        "name": "review_pull_request",
        "description": "Review a pull request and post a structured review comment.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_owner": {
                    "type": "string",
                    "description": "Owner of the repository",
                },
                "repo_name": {
                    "type": "string",
                    "description": "Name of the repository",
                },
                "pr_number": {
                    "type": "integer",
                    "description": "Pull request number",
                },
                "title": {
                    "type": "string",
                    "description": "Title of the PR",
                },
                "description": {
                    "type": "string",
                    "description": "Description of changes",
                },
                "unmet_requirements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of unmet requirements",
                },
                "test_evaluation": {
                    "type": "object",
                    "description": "Dictionary with test evaluation details",
                    "properties": {
                        "failed": {"type": "array", "items": {"type": "string"}},
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
                "staking_key": {
                    "type": "string",
                    "description": "Reviewer's staking key",
                },
                "pub_key": {
                    "type": "string",
                    "description": "Reviewer's public key",
                },
                "staking_signature": {
                    "type": "string",
                    "description": "Reviewer's staking signature",
                },
                "public_signature": {
                    "type": "string",
                    "description": "Reviewer's public signature",
                },
            },
            "required": [
                "repo_owner",
                "repo_name",
                "pr_number",
                "title",
                "description",
                "unmet_requirements",
                "test_evaluation",
                "recommendation",
                "recommendation_reason",
                "action_items",
                "staking_key",
                "pub_key",
                "staking_signature",
                "public_signature",
            ],
        },
        "final_tool": True,
        "function": review_pull_request,
    },
    "validate_implementation": {
        "name": "validate_implementation",
        "description": "Validate that an implementation meets its requirements.",
        "parameters": {
            "type": "object",
            "properties": {
                "validated": {
                    "type": "boolean",
                    "description": "Whether the implementation passed validation",
                },
                "test_results": {
                    "type": "object",
                    "description": "Results from running tests",
                    "properties": {
                        "passed": {"type": "array", "items": {"type": "string"}},
                        "failed": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "criteria_status": {
                    "type": "object",
                    "description": "Status of each acceptance criterion",
                    "properties": {
                        "met": {"type": "array", "items": {"type": "string"}},
                        "not_met": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "directory_check": {
                    "type": "object",
                    "description": "Results of directory structure validation",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "issues": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of issues found during validation",
                },
                "required_fixes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of fixes needed to meet requirements",
                },
            },
            "required": [
                "validated",
                "test_results",
                "criteria_status",
                "directory_check",
                "issues",
                "required_fixes",
            ],
        },
        "final_tool": True,
        "function": validate_implementation,
    },
    "generate_analysis": {
        "name": "generate_analysis",
        "description": "Analyze a repository for bugs, security vulnerabilities, and code quality issues.",
        "parameters": {
            "type": "object",
            "properties": {
                "bugs": {
                    "type": "array",
                    "description": "List of bugs found in the repository",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "A full description of the bug with enough information to fix it",
                            },
                            "acceptance_criteria": {
                                "type": "array",
                                "description": "A list of acceptance criteria, comprehensive enough to confirm the fix",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
                "vulnerabilities": {
                    "type": "array",
                    "description": "List of vulnerabilities found in the repository",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "A full description of the vulnerability with enough "
                                "information to fix it",
                            },
                            "acceptance_criteria": {
                                "type": "array",
                                "description": "A list of acceptance criteria, comprehensive enough to confirm the fix",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
                "code_quality_issues": {
                    "type": "array",
                    "description": "List of code quality issues found in the repository",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "A full description of the code quality issue with enough "
                                "information to fix it",
                            },
                            "acceptance_criteria": {
                                "type": "array",
                                "description": "A list of acceptance criteria, comprehensive enough to confirm the fix",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
                "file_name": {
                    "type": "string",
                    "description": "Name of the output file",
                },
            },
            "required": ["bugs", "vulnerabilities", "code_quality_issues", "file_name"],
        },
        "final_tool": True,
        "function": generate_analysis,
    },
    "merge_pull_request": {
        "name": "merge_pull_request",
        "description": "Merge a pull request using the GitHub API.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_full_name": {
                    "type": "string",
                    "description": "Full name of repository (owner/repo)",
                },
                "pr_number": {
                    "type": "integer",
                    "description": "Pull request number to merge",
                },
                "merge_method": {
                    "type": "string",
                    "description": "Merge method to use (merge, squash, rebase)",
                    "enum": ["merge", "squash", "rebase"],
                    "default": "merge",
                },
            },
            "required": ["repo_full_name", "pr_number"],
        },
        "function": merge_pull_request,
    },
    "generate_tasks": {
        "name": "generate_tasks",
        "description": "Generate a CSV file containing tasks from a feature breakdown.",
        "parameters": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "description": "List of subtasks from the feature breakdown",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Clear, specific title of the task",
                                "maxLength": 100,
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed explanation of the work required",
                                "minLength": 10,
                            },
                            "acceptance_criteria": {
                                "type": "array",
                                "description": "List of verifiable acceptance criteria",
                                "items": {"type": "string", "minLength": 1},
                                "minItems": 1,
                            },
                        },
                    },
                }
            },
            "required": ["tasks"],
        },
        "final_tool": True,
        "function": generate_tasks,
    },
}
