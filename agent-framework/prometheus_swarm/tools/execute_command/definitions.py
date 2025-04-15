from prometheus_swarm.tools.execute_command.implementations import (
    execute_command,
    run_tests,
    install_dependency,
    setup_dependencies,
)


DEFINITIONS = {
    "execute_command": {
        "name": "execute_command",
        "description": "Execute a shell command in the current working directory",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute",
                }
            },
            "required": ["command"],
        },
        "function": execute_command,
    },
    "run_tests": {
        "name": "run_tests",
        "description": "Run tests using a specified framework.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to test file or directory.",
                },
                "framework": {
                    "type": "string",
                    "description": "Test framework to use.",
                    "enum": ["pytest", "jest", "vitest"],
                },
            },
            "required": ["framework", "path"],
        },
        "function": run_tests,
    },
    "install_dependency": {
        "name": "install_dependency",
        "description": "Install a dependency using the specified package manager with appropriate flags",
        "parameters": {
            "type": "object",
            "properties": {
                "package_name": {
                    "type": "string",
                    "description": "Name of the package to install",
                },
                "package_manager": {
                    "type": "string",
                    "description": "Package manager to use",
                    "enum": ["npm", "pip", "yarn", "pnpm"],
                },
                "is_dev_dependency": {
                    "type": "boolean",
                    "description": "Whether to install as a dev dependency (where applicable)",
                    "default": False,
                },
                "version": {
                    "type": "string",
                    "description": "Specific version to install (optional)",
                },
            },
            "required": ["package_name", "package_manager"],
        },
        "function": install_dependency,
    },
    "setup_dependencies": {
        "name": "setup_dependencies",
        "description": "Install all required dependencies for the project",
        "parameters": {
            "type": "object",
            "properties": {
                "package_manager": {
                    "type": "string",
                    "description": "Package manager to use",
                    "enum": ["npm", "pip", "yarn", "pnpm"],
                },
            },
            "required": ["package_manager"],
        },
        "function": setup_dependencies,
    },
}
