"""Task decomposition workflow phases implementation."""

from enum import Enum
from src.workflows.base import WorkflowPhase, Workflow


class RepoType(Enum):
    LIBRARY = "library"
    WEB_APP = "web_app"
    API_SERVICE = "api_service"
    MOBILE_APP = "mobile_app"
    TUTORIAL = "tutorial"
    TEMPLATE = "template"
    CLI_TOOL = "cli_tool"
    FRAMEWORK = "framework"
    DATA_SCIENCE = "data_science"
    OTHER = "other"


class ReadmeGenerationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="generate_readme_file",
            available_tools=[
                "read_file",
                "write_file",
                "list_files",
                "commit_and_push",
            ],
            conversation_id=conversation_id,
            name="Readme Generation",
        )


class RepoClassificationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="classify_repository",
            available_tools=["read_file", "list_files", "get_readme_prompt"],
            conversation_id=conversation_id,
            name="Repository Classification",
        )


class CreatePullRequestPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_pull_request",
            required_tool="create_pull_request",
            conversation_id=conversation_id,
            name="Create Pull Request",
        )
