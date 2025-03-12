"""Base classes for workflow implementation."""

from typing import Optional, Dict, Any, List, Type, Union, get_args, get_origin
from abc import ABC, abstractmethod
import ast
from dataclasses import dataclass
from functools import wraps
from src.types import ToolResponse, PhaseResult
from src.utils.retry import send_message_with_retry
from src.utils.logging import log_section, log_error


@dataclass
class ContextRequirements:
    """Documents where context variables are used in a phase with their types"""

    templates: Dict[str, Type]  # Variables used in templates and their types
    tools: Dict[str, Type]  # Variables used in tool calls and their types

    @property
    def all_vars(self) -> Dict[str, Type]:
        """All required variables and their types"""
        return {**self.templates, **self.tools}


def requires_context(
    *, templates: Dict[str, Type] = None, tools: Dict[str, Type] = None
):
    """Decorator to specify context requirements with types"""

    def decorator(phase_class):
        phase_class.context_requirements = ContextRequirements(
            templates=templates or {}, tools=tools or {}
        )

        def validate_type(value: Any, expected_type: Type) -> bool:
            """Validate a value against an expected type, handling Union and Optional"""
            if expected_type is Any:
                return True

            # Handle Optional[Type] and Union[Type, None]
            if get_origin(expected_type) is Union:
                types = get_args(expected_type)
                # If None is one of the types, it's Optional
                if type(None) in types:
                    if value is None:
                        return True
                    # Remove None from types for checking
                    other_types = tuple(t for t in types if t is not type(None))
                    return isinstance(value, other_types)
                return isinstance(value, types)

            return isinstance(value, expected_type)

        # Wrap the original __init__ to validate context
        original_init = phase_class.__init__

        @wraps(original_init)
        def wrapped_init(self, *args, **kwargs):
            workflow = kwargs.get("workflow") or args[0]

            # Check all required variables exist with correct types
            type_errors = []
            missing = []

            for var, expected_type in self.context_requirements.all_vars.items():
                if var not in workflow.context:
                    missing.append(var)
                    continue

                value = workflow.context[var]
                if not validate_type(value, expected_type):
                    type_errors.append(
                        f"{var}: expected {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )

            if missing or type_errors:
                error_msg = []
                if missing:
                    error_msg.append(
                        f"Missing context in {phase_class.__name__}: {missing}"
                    )
                if type_errors:
                    error_msg.append(
                        f"Type errors in {phase_class.__name__}: {type_errors}"
                    )
                error_msg.append(
                    f"\nTemplate vars: {self.context_requirements.templates}"
                )
                error_msg.append(f"Tool vars: {self.context_requirements.tools}")
                raise ValueError("\n".join(error_msg))

            original_init(self, *args, **kwargs)

        phase_class.__init__ = wrapped_init
        return phase_class

    return decorator


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
