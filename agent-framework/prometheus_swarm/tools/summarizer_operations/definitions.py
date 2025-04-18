"""Summarizer operations tool definitions."""

from prometheus_swarm.tools.summarizer_operations.implementations import (
    create_readme_file,
    review_readme_file,
)

DEFINITIONS = {
    "create_readme_file": {
        "name": "create_readme_file",
        "description": "Create a README file in the repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "readme_content": {
                    "type": "string",
                    "description": "The content of the README file",
                },
            },
            "required": ["readme_content"],
        },
        "function": create_readme_file,
    },
    "review_readme_file": {
        "name": "review_readme_file",
        "description": "Review the README file and provide a recommendation and comment.",
        "parameters": {
            "type": "object",
            "properties": {
                "recommendation": {
                    "type": "string",
                    "description": "APPROVE/REVISE/REJECT",
                },
                "comment": {
                    "type": "string",
                    "description": "The comment to create on the README file",
                },
            },
            "required": ["recommendation", "comment"],
        },
        "function": review_readme_file,
    },
}
