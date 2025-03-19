"""Base classes for workflow implementation."""

from typing import Optional, Dict, Any, List, Type, Union, get_args, get_origin
from abc import ABC, abstractmethod
import ast
from dataclasses import dataclass
from functools import wraps
from src.types import ToolResponse, PhaseResult
from src.utils.retry import send_message_with_retry
from src.utils.logging import log_section, log_error, configure_logging
from src.clients import clients, setup_client
import argparse
import sys
import os


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
            """Validate a value against an expected type, handling Union, Optional, and generics"""
            if expected_type is Any:
                return True

            # Get the origin type (e.g., list for List[str])
            origin = get_origin(expected_type)
            if origin is not None:
                # Handle Optional[Type] and Union[Type, None]
                if origin is Union:
                    types = get_args(expected_type)
                    # If None is one of the types, it's Optional
                    if type(None) in types:
                        if value is None:
                            return True
                        # Remove None from types for checking
                        other_types = tuple(t for t in types if t is not type(None))
                        return any(validate_type(value, t) for t in other_types)
                    return any(validate_type(value, t) for t in types)

                # Handle other generic types (List, Dict, etc.)
                if not isinstance(value, origin):
                    return False

                # Get the type arguments (e.g., str for List[str])
                args = get_args(expected_type)
                if not args:
                    return True

                # For lists, check each element
                if origin is list:
                    return all(validate_type(item, args[0]) for item in value)

                # For dicts, check key and value types
                if origin is dict:
                    key_type, value_type = args
                    return all(
                        validate_type(k, key_type) and validate_type(v, value_type)
                        for k, v in value.items()
                    )

                # For other generic types, just check the base type
                return True

            # For non-generic types, use isinstance
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
        else:
            # Update tools for existing conversation
            workflow.client.storage.update_tools(
                conversation_id=self.conversation_id,
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


class WorkflowExecution(ABC):
    """Base class for workflow execution."""

    def __init__(
        self,
        description: str,
        additional_arguments: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """Initialize the workflow execution.

        Args:
            description: Description of the workflow for help text
            additional_arguments: Optional dictionary of additional arguments to add to parser.
                                Format: {"arg_name": {"type": type, "help": "help text", **other_argparse_kwargs}}
        """
        self.description = description
        self.context: Dict[str, Any] = {}

        # Create parser and parse args immediately
        parser = argparse.ArgumentParser(description=self.description)

        # Add common arguments
        parser.add_argument(
            "--model",
            type=str,
            default="anthropic",
            choices=list(clients.keys()),
            help=f"Model provider to use (default: anthropic). Available models: {', '.join(clients.keys())}",
        )

        # Add workflow-specific arguments
        for arg_name, arg_config in (additional_arguments or {}).items():
            parser.add_argument(f"--{arg_name}", **arg_config)

        # Parse args immediately since these scripts are always run directly
        self.args = parser.parse_args()

    def _setup(
        self,
        required_env_vars: Optional[List[str]] = None,
        prompts=None,
    ):
        """Set up workflow context and resources.

        Args:
            required_env_vars: List of required environment variables
            prompts: Dictionary of prompts for this workflow

        This base implementation:
        1. Sets up logging
        2. Checks required environment variables
        3. Sets up client and prompts

        Override this method to add workflow-specific setup, calling super()._setup() first.
        """
        # Set up logging
        configure_logging()

        # Check env vars
        if required_env_vars:
            self._check_env_vars(required_env_vars)

        # Set up common context
        self.context["client"] = setup_client(self.args.model)
        if prompts:
            self.context["prompts"] = prompts

    def _check_env_vars(self, required_vars: List[str]):
        """Check if required environment variables are set.

        Args:
            required_vars: List of required environment variable names

        Raises:
            EnvironmentError: If any required variables are missing
        """
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    def _parse_github_url(self, url: str) -> tuple[str, str]:
        """Parse a GitHub repository URL into owner and repo name.

        Args:
            url: GitHub repository URL (e.g., https://github.com/owner/repo)

        Returns:
            tuple[str, str]: (owner, repo_name)

        Raises:
            ValueError: If URL format is invalid
        """
        parts = url.strip("/").split("/")
        if len(parts) < 5 or parts[2] != "github.com":
            raise ValueError(
                "Invalid repository URL format. Use https://github.com/owner/repo"
            )
        return parts[-2], parts[-1]

    @abstractmethod
    def _run(self):
        """Run the workflow.

        Override this to execute the workflow with the prepared context.
        """
        pass

    def start(self):
        """Execute the workflow.

        This orchestrates the full execution flow:
        1. Run setup
        2. Run the workflow

        This is the main public interface for running workflows.
        """
        try:
            # Run setup
            self._setup()

            # Run workflow
            self._run()

        except Exception as e:
            log_error(e, "Workflow failed")
            sys.exit(1)
