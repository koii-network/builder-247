"""Repository operations tool definitions."""

from prometheus_swarm.tools.repo_operations.implementations import (
    classify_repository,
    classify_language,
    classify_test_framework,
)
from prometheus_swarm.tools.repo_operations.Types import RepoType, Language, TestFramework

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
                    "enum": RepoType.to_string_list(),
                },
            },
            "required": ["repo_type"],
            "additionalProperties": False,
        },
        "final_tool": True,
        "function": classify_repository,
    },
    "classify_language": {
        "name": "classify_language",
        "description": "Classify a repository into a specific language",
        "parameters": {
            "type": "object",
            "properties": { 
                "language": {
                    "type": "string",
                    "description": "The language, must be one of: python, javascript, java, c, go, rust, ruby, php, swift, kotlin, scala, r, shell, other",
                    "enum": Language.to_string_list(),
                },
            },
            "required": ["language"],
            "additionalProperties": False,
        },
        "final_tool": True,
        "function": classify_language,
    },
    "classify_test_framework": {
        "name": "classify_test_framework",
        "description": "Classify a repository into a specific test framework",
        "parameters": {
            "type": "object",
            "properties": {
                "test_framework": {
                    "type": "string",
                    "description": "The test framework, must be one of: pytest, unittest, jest, mocha, junit, testng, go_testing, rspec, phpunit, xctest, kotest, other",
                    "enum": TestFramework.to_string_list(),
                },  
            },
            "required": ["test_framework"],
            "additionalProperties": False,
        },
        "final_tool": True,
        "function": classify_test_framework,
    },
}