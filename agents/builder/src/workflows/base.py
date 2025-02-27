"""Base classes for workflow implementation."""

from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import ast
from src.types import ToolResponse, PhaseResult
from src.utils.retry import send_message_with_retry
from src.utils.logging import log_section, log_error
from src.workflows.prompts import PROMPTS


class WorkflowPhase:

    def __init__(
        self,
        workflow=None,
        prompt_name: str = "",
        available_tools: Optional[List[str]] = None,
        required_tool: Optional[str] = None,
        conversation_id: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self.available_tools = available_tools
        self.required_tool = required_tool
        self.conversation_id = conversation_id
        self.workflow = workflow
        self.prompt = PROMPTS[prompt_name].format(**workflow.context)
        self.name = name or self.__class__.__name__

    @classmethod
    def create(cls, workflow, **kwargs):
        """Factory method to create a phase with the workflow."""
        instance = cls(**kwargs)
        instance.workflow = workflow  # Set the workflow after initialization
        return instance

    def _parse_result(self, tool_response: ToolResponse) -> PhaseResult:
        """Parse raw API response into standardized format"""
        try:
            response_data = ast.literal_eval(tool_response.get("response", "{}"))
            return PhaseResult(
                success=response_data.get("success", False),
                data=response_data.get("data", {}),
                error=(
                    response_data.get("message")
                    if not response_data.get("success")
                    else None
                ),
            )
        except (SyntaxError, ValueError) as e:
            return PhaseResult(
                success=False,
                data={},
                error=f"Failed to parse response: {str(e)}",
            )

    def execute(self):
        """Run the phase."""
        log_section(f"RUNNING PHASE: {self.name}")

        workflow = self.workflow

        if not workflow:
            raise ValueError("Workflow is not set")

        # Create new conversation if needed
        if self.conversation_id is None:
            self.conversation_id = workflow.client.create_conversation(
                system_prompt=workflow.system_prompt,
                available_tools=self.available_tools,
            )

        # Handle required tools
        tool_choice = {"type": "auto"}
        if self.required_tool:
            tool_choice = {"type": "required", "tool": self.required_tool}

        response = send_message_with_retry(
            workflow.client,
            prompt=self.prompt,
            conversation_id=self.conversation_id,
            tool_choice=tool_choice,
        )

        results = workflow.client.handle_tool_response(response)
        if not results:
            log_error(
                Exception("No results returned from phase"),
                f"Phase {self.name} failed",
            )
            return None

        return self._parse_result(results[-1])  # Return the last result


class Workflow(ABC):
    def __init__(self, client, system_prompt: Optional[str] = None, **kwargs):
        if not client:
            raise ValueError("Workflow client is not set")

        self.client = client
        self.system_prompt = system_prompt
        self.context: Dict[str, Any] = kwargs

    @abstractmethod
    def setup(self):
        """Non-agent setup steps."""
        pass

    @abstractmethod
    def run(self):
        """Main workflow implementation."""
        pass

    def cleanup(self):
        """Cleanup steps."""
        pass
