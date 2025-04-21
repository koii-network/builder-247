"""Task decomposition workflow phases implementation."""

from prometheus_swarm.workflows.base import WorkflowPhase, Workflow



class RepoClassificationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="classify_repository",
            available_tools=["read_file", "list_files", "classify_repository", ],
            conversation_id=conversation_id,
            name="Repository Classification",
        )

class LanguageClassificationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="classify_language",
            available_tools=["read_file", "list_files", "classify_language"],
            conversation_id=conversation_id,
            name="Language Classification",
        )   

class TestFrameworkClassificationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="classify_test_framework",
            available_tools=["read_file", "list_files", "classify_test_framework"],
            conversation_id=conversation_id,
            name="Test Framework Classification",
        )   

class ReadmeGenerationPhase(WorkflowPhase):
    def __init__(self, workflow: Workflow, conversation_id: str = None):
        super().__init__(
            workflow=workflow,
            prompt_name="generate_readme",
            available_tools=["read_file", "list_files", "generate_readme"],
            conversation_id=conversation_id,
            name="Readme Generation",
        )



