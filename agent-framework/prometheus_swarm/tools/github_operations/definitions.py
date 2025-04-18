from prometheus_swarm.tools.github_operations.implementations import (
    create_worker_pull_request,
    create_leader_pull_request,
    review_pull_request,
    review_pull_request_legacy,
    validate_implementation,
    generate_analysis,
    merge_pull_request,
    create_github_issue,
    star_repository,
    create_pull_request_legacy
)

DEFINITIONS = {
    "create_worker_pull_request": {
        "name": "create_worker_pull_request",
        "description": "Create a pull request for a worker node with task implementation details and signatures.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the pull request",
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
            },
            "required": [
                "title",
                "description",
                "changes",
                "tests",
                "todo",
            ],
        },
        "function": create_worker_pull_request,
    },
    "create_pull_request_legacy": {
        "name": "create_pull_request_legacy",
        "description": "Create a pull request with formatted description.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the pull request"},
                "description": {
                    "type": "string",
                    "description": "A brief summary of the changes made",
                },
                "github_token": {
                    "type": "string",
                    "description": "GitHub token for authentication",
                },
            },
            "required": ["title", "description", "github_token"],
        },
        "final_tool": True,
        "function": create_pull_request_legacy,
    },
    
    "create_leader_pull_request": {
        "name": "create_leader_pull_request",
        "description": "Create a pull request for a leader node consolidating multiple worker PRs.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Clear and descriptive title summarizing the main themes of the changes",
                },
                "description": {
                    "type": "string",
                    "description": "High-level explanation of the overall purpose and benefits of the changes",
                },
                "changes": {
                    "type": "string",
                    "description": "Description of major functional and architectural changes made",
                },
                "tests": {
                    "type": "string",
                    "description": "Description of verification steps taken and test coverage",
                },
            },
            "required": ["title", "description", "changes", "tests"],
        },
        "function": create_leader_pull_request,
    },
    "review_pull_request": {
        "name": "review_pull_request",
        "description": "Review a pull request and post a structured review comment.",
        "parameters": {
            "type": "object",
            "properties": {
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
            },
            "required": [
                "title",
                "description",
                "unmet_requirements",
                "test_evaluation",
                "recommendation",
                "recommendation_reason",
                "action_items",
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
    "create_github_issue": {
        "name": "create_github_issue",
        "description": "Create a GitHub issue.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_full_name": {
                    "type": "string",
                    "description": "Full name of repository (owner/repo)",
                },
                "title": {
                    "type": "string",
                    "description": "Issue title",
                },
                "description": {
                    "type": "string",
                    "description": "Issue description",
                },
            },
            "required": ["repo_full_name", "title", "description"],
        },
        "final_tool": True,
        "function": create_github_issue,
    },
    "star_repository": {
        "name": "star_repository",
        "description": "Star a repository using the GitHub API.",
        "parameters": {
            "type": "object",
            "properties": {
                "owner": {"type": "string", "description": "Owner of the repository"},
                "repo_name": {
                    "type": "string",
                    "description": "Name of the repository",
                },
            },
            "required": ["owner", "repo_name"],
        },
        "function": star_repository,
    },

    "review_pull_request_legacy": {
        "name": "review_pull_request_legacy",
        "description": "Review a pull request and post a structured review comment.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the PR"},
                "description": {
                    "type": "string",
                    "description": "Description of changes",
                },
                "recommendation": {
                    "type": "string",
                    "description": "Decision to approve, revise, or reject the PR",
                    "enum": ["APPROVE", "REVISE", "REJECT"],
                },
                "recommendation_reason": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Reasons for recommendation",
                },
            },
            "required": [
                "title",
                "description",
                "recommendation",
                "recommendation_reason",
            ],
        },
        "final_tool": True,
        "function": review_pull_request_legacy,
    },
}
