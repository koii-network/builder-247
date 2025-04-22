from prometheus_swarm.tools.planner_operations.implementations import (
    generate_tasks,
    validate_tasks,
    regenerate_tasks,
    create_task_dependency,
    generate_issues,
    audit_tasks,
)

DEFINITIONS = {
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
            "additionalProperties": False,
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
                        "required": ["title", "description", "acceptance_criteria", "uuid"],
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
    "audit_tasks": {
        "name": "audit_tasks",
        "description": "Audit the tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {
                    "type": "boolean",
                    "description": "Result of the validation",
                },
            },
            "required": ["result"],
            "additionalProperties": False,
        },
        "final_tool": True,
        "function": audit_tasks,
    },
}
