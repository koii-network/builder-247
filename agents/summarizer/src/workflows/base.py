"""Base classes for workflow implementation."""

from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import ast
from src.types import ToolResponse, PhaseResult
from src.utils.retry import send_message_with_retry
from src.utils.logging import log_section, log_error


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
        """Initialize a workflow phase.

        If workflow is provided, the prompt will be formatted with the workflow context.
        """
        self.available_tools = available_tools
        self.required_tool = required_tool
        self.conversation_id = conversation_id
        self.prompt_name = prompt_name
        self.name = name or self.__class__.__name__
        self.workflow = workflow

        # Format the prompt if workflow is provided
        self.prompt = None

        if workflow is None:
            raise ValueError("Workflow is not set")

        self.prompt = workflow.prompts[prompt_name].format(**workflow.context)

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
                system_prompt=workflow.prompts["system_prompt"],
                available_tools=self.available_tools,
            )

        # Handle required tools
        tool_choice = {"type": "optional"}
        if self.required_tool:
            tool_choice = {"type": "required", "tool": self.required_tool}

        response = send_message_with_retry(
            workflow.client,
            prompt=self.prompt,
            conversation_id=self.conversation_id,
            tool_choice=tool_choice,
        )

        results = workflow.client.handle_tool_response(
            response, context=workflow.context
        )
        if not results:
            log_error(
                Exception("No results returned from phase"),
                f"Phase {self.name} failed",
            )
            return None

        phase_result = self._parse_result(results[-1])  # Return the last result

        if not phase_result.get("success"):
            log_error(Exception(phase_result.get("error")), f"Phase {self.name} failed")
            return None

        return phase_result


class Workflow(ABC):
    def __init__(self, client, prompts, **kwargs):
        if not client:
            raise ValueError("Workflow client is not set")

        self.client = client
        self.prompts = prompts
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
