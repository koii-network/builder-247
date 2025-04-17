"""Repository operations tool definitions."""

from prometheus_swarm.tools.repo_operations.implementations import classify_repository

DEFINITIONS = {
    "classify_repository": {
        "name": "classify_repository",
        "description": "Classify a repository into a specific type",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_type": {
                    "type": "string",
                    "description": "The repository type, must be one of: library, web_app, api_service, mobile_app, "
                    "tutorial, template, cli_tool, framework, data_science, other",
                    "enum": [
                        "library",
                        "web_app",
                        "api_service",
                        "mobile_app",
                        "tutorial",
                        "template",
                        "cli_tool",
                        "framework",
                        "data_science",
                        "plugin",
                        "chrome_extension",
                        "jupyter_notebook",
                        "infrastructure",
                        "smart_contract",
                        "dapp",
                        "game",
                        "desktop_app",
                        "dataset",
                        "other",
                    ],
                },
            },
            "required": ["repo_type"],
        },
        "required": ["repo_type"],
        "final_tool": True,
        "function": classify_repository,
    },
}
