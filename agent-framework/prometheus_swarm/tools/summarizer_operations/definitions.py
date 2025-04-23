"""Summarizer operations tool definitions."""

from prometheus_swarm.tools.summarizer_operations.implementations import (
    create_readme_file,
    create_readme_section,
    review_readme_file,
)

DEFINITIONS = {
    "create_readme_section": {
        "name": "create_readme_section",
        "description": "Create a section of a README file.",
        "parameters": {
            "type": "object",
            "properties": {
                "section_content": {
                    "type": "string",
                    "description": "The content of the section to create",
                },
            },
            "required": ["section_content"],
        },
        "function": create_readme_section,
        "final_tool": True,
    },
    "create_readme_file": {
        "name": "create_readme_file",
        "description": "Create a README file.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the README file",
                },
            },
            "required": ["title"],
        },
        "function": create_readme_file,
        "final_tool": True,
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
