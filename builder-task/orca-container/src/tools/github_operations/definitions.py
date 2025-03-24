from src.tools.github_operations.implementations import (
    create_worker_pull_request,
    create_leader_pull_request,
    generate_issues,
    review_pull_request,
    validate_implementation,
    generate_analysis,
    merge_pull_request,
    generate_tasks,
    validate_tasks,
    regenerate_tasks,
    create_task_dependency,
    create_github_issue,
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
    "generate_tasks": {
        "name": "generate_tasks",
        "description": "Generate a JSON file containing tasks from a feature breakdown.",
        "parameters": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "description": "List of tasks",
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
                        "required": ["title", "description", "acceptance_criteria"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["tasks"],
        },
        "final_tool": True,
        "function": generate_tasks,
    },
    "regenerate_tasks": {
        "name": "regenerate_tasks",
        "description": "Regenerate the tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "description": "List of tasks",
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
                            "uuid": {
                                "type": "string",
                                "description": "UUID of the task",
                            },
                        },
                        "required": [
                            "title",
                            "description",
                            "acceptance_criteria",
                            "uuid",
                        ],
                        "additionalProperties": False,
                    },
                },
                # "file_name": {
                #     "type": "string",
                #     "description": "Name of the output JSON file",
                #     "default": "tasks.json",
                # },
                # "repo_url": {
                #     "type": "string",
                #     "description": "URL of the repository (for reference)",
                # },
            },
            "required": ["tasks"],
            "additionalProperties": False,
        },
        "final_tool": True,
        "function": regenerate_tasks,
    },
    "validate_tasks": {
        "name": "validate_tasks",
        "description": "Generate a List of Decisions on Tasks from a feature breakdown.",
        "parameters": {
            "type": "object",
            "properties": {
                "decisions": {
                    "type": "array",
                    "description": "List of decisions on tasks",
                    "items": {
                        "type": "object",
                        "properties": {
                            "uuid": {
                                "type": "string",
                                "description": "UUID of the task",
                            },
                            "comment": {
                                "type": "string",
                                "description": "Comment on the task",
                            },
                            "decision": {
                                "type": "boolean",
                            },
                        },
                        "required": ["uuid", "comment", "decision"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["decisions"],
            "additionalProperties": False,
        },
        "final_tool": True,
        "function": validate_tasks,
    },
    "create_task_dependency": {
        "name": "create_task_dependency",
        "description": "Create the task dependency for a task.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_uuid": {
                    "type": "string",
                    "description": "UUID of the task",
                },
                "dependency_tasks": {
                    "type": "array",
                    "description": "List of UUIDs of dependency tasks",
                },
            },
            "required": ["task_uuid", "dependency_tasks"],
            "additionalProperties": False,
        },
        "final_tool": True,
        "function": create_task_dependency,
    },
    "generate_issues": {
        "name": "generate_issues",
        "description": "Generate a JSON file containing issues from a feature breakdown.",
        "parameters": {
            "type": "object",
            "properties": {
                "issues": {
                    "type": "array",
                    "description": "List of issues",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Clear, specific title of the issue",
                                "maxLength": 100,
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed explanation of the issue",
                                "minLength": 10,
                            },
                        },
                        "required": ["title", "description"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["issues"],
            "additionalProperties": False,
        },
        "final_tool": True,
        "function": generate_issues,
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
}
