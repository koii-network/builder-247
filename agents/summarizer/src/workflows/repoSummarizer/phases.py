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


class BranchCreationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_branch",
            available_tools=["create_branch"],
            conversation_id=conversation_id,
            name="Branch Creation",
        )


class RepoClassificationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="classify_repository",
            available_tools=["read_file", "list_files", "classify_repository"],
            conversation_id=conversation_id,
            name="Repository Classification",
        )


class ReadmeGenerationPhase(WorkflowPhase):
    def __init__(
        self, workflow: Workflow, conversation_id: str = None, prompt_name: str = None
    ):
        super().__init__(
            workflow=workflow,
            prompt_name=prompt_name,
            available_tools=[
                "read_file",
                "list_files",
                "write_file",
            ],
            conversation_id=conversation_id,
            name="Readme Generation",
            max_tokens=8192,
        )


class CreatePullRequestPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_pr",
            available_tools=["read_file", "list_files", "create_pull_request"],
            conversation_id=conversation_id,
            name="Create Pull Request",
        )
