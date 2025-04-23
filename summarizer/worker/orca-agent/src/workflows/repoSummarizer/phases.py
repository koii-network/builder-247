"""Task decomposition workflow phases implementation."""

from prometheus_swarm.workflows.base import WorkflowPhase, Workflow


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


class ReadmeSectionGenerationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="generate_readme_section",
            available_tools=[
                "read_file",
                "list_files",
                "create_readme_section",
            ],
            conversation_id=conversation_id,
            name="Readme Section Generation",
        )


class ReadmeFileCreationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="generate_readme",
            required_tool="create_readme_file",
            conversation_id=conversation_id,
            name="Readme File Creation",
        )


class ReadmeReviewPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="review_readme_file",
            available_tools=["read_file", "list_files", "review_readme_file"],
            conversation_id=conversation_id,
            name="Readme Review",
        )


class CreatePullRequestPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="create_pr",
            available_tools=["read_file", "list_files", "create_pull_request_legacy"],
            conversation_id=conversation_id,
            name="Create Pull Request",
        )
