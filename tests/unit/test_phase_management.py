"""Unit tests for phase management functionality."""

import pytest
from unittest.mock import Mock

from src.phase_management import (
    ImplementationPhase,
    PhaseState,
    PhaseManager,
)
from src.tools.types import ToolResponse, ToolResponseStatus
from src.utils.monitoring import ToolLogger


def test_phase_state_initialization():
    """Test PhaseState initialization with default values."""
    state = PhaseState(phase=ImplementationPhase.ANALYSIS)
    assert state.phase == ImplementationPhase.ANALYSIS
    assert state.attempts == 0
    assert state.last_error is None
    assert state.last_feedback is None


def test_phase_state_with_values():
    """Test PhaseState initialization with custom values."""
    state = PhaseState(
        phase=ImplementationPhase.IMPLEMENTATION,
        attempts=2,
        last_error="Test error",
        last_feedback="Test feedback",
    )
    assert state.phase == ImplementationPhase.IMPLEMENTATION
    assert state.attempts == 2
    assert state.last_error == "Test error"
    assert state.last_feedback == "Test feedback"


class TestPhaseManager:
    """Test suite for PhaseManager class."""

    @pytest.fixture
    def mock_tools(self):
        """Create mock tools implementation."""
        return Mock()

    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock(spec=ToolLogger)

    @pytest.fixture
    def phase_manager(self, mock_tools, mock_logger):
        """Create PhaseManager instance with mocked dependencies."""
        return PhaseManager(tools=mock_tools, logger=mock_logger)

    def test_initialization(self, phase_manager, mock_tools, mock_logger):
        """Test PhaseManager initialization."""
        assert phase_manager.tools == mock_tools
        assert phase_manager.logger == mock_logger
        assert phase_manager.max_retries == 3

    def test_run_phase_with_recovery_success(self, phase_manager):
        """Test successful phase execution."""
        phase_state = PhaseState(phase=ImplementationPhase.ANALYSIS)
        context = {"test": "data"}

        # Mock successful execution
        phase_manager._execute_tools = Mock(return_value={"status": "success"})
        phase_manager._validate_phase = Mock(return_value={"status": "success"})

        result = phase_manager.run_phase_with_recovery(phase_state, context)

        assert result == {"status": "success"}
        assert phase_state.attempts == 1
        assert phase_state.last_error is None

    def test_run_phase_with_recovery_failure(self, phase_manager):
        """Test phase execution with failure and retry."""
        phase_state = PhaseState(phase=ImplementationPhase.ANALYSIS)
        context = {"test": "data"}

        # Mock failed execution
        phase_manager._execute_tools = Mock(return_value=None)

        result = phase_manager.run_phase_with_recovery(phase_state, context)

        assert result is None
        assert phase_state.attempts == 1
        assert phase_state.last_error is not None

    def test_execute_tool_safely(self, phase_manager):
        """Test safe tool execution."""
        tool_call = {"name": "test_tool", "parameters": {"param": "value"}}

        # Mock successful tool execution
        phase_manager.tools.execute = Mock(
            return_value=ToolResponse(
                status=ToolResponseStatus.SUCCESS, output="test output"
            )
        )

        response = phase_manager._execute_tool_safely(tool_call)

        assert response.status == ToolResponseStatus.SUCCESS
        assert response.output == "test output"

    def test_create_message_with_context(self, phase_manager):
        """Test message creation with context."""
        context = {"test": "data"}
        phase_state = PhaseState(
            phase=ImplementationPhase.ANALYSIS, last_feedback="Previous feedback"
        )

        message = phase_manager._create_message_with_context(context, phase_state)

        assert isinstance(message, str)
        assert "Previous feedback" in message
