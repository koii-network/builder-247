"""Template for organizing related tests using pytest.

This template demonstrates:
1. Using classes to group related test cases
2. Descriptive docstrings that explain test purpose and assumptions
3. Using pytest markers to categorize tests
4. Shared fixtures for common setup
5. Clear naming conventions
"""

import pytest
from tests.utils.fixtures import workspace_dir  # Import common fixture


# Define custom markers for test categories
pytestmark = [
    pytest.mark.component("example"),  # Component being tested
    pytest.mark.integration,  # Test type
]


@pytest.fixture
def example_fixture(workspace_dir):
    """Setup for tests in this module.

    Args:
        workspace_dir: Standard workspace fixture

    Returns:
        Dict containing test data
    """
    return {"test_data": "example"}


class TestFeatureGroup:
    """Group of tests for a specific feature/component.

    Tests in this class verify:
    - Core functionality X
    - Edge cases for X
    - Error handling for X

    Related test modules:
    - test_other_feature.py - Tests dependent functionality
    - test_integration.py - Tests integration with other components
    """

    @pytest.fixture(autouse=True)
    def setup(self, example_fixture):
        """Setup shared by all tests in this class."""
        self.data = example_fixture

    def test_main_functionality(self):
        """Verify core functionality works as expected.

        Requirements:
        1. System should do X when given Y
        2. Output should match Z format

        Assumptions:
        - Component A is properly initialized
        - Input data follows schema B
        """
        # Test implementation
        pass

    @pytest.mark.parametrize("input,expected", [("valid", True), ("invalid", False)])
    def test_edge_cases(self, input: str, expected: bool):
        """Verify behavior for edge cases.

        This test verifies the system handles various inputs correctly:
        - Valid inputs within normal range
        - Invalid/malformed inputs
        - Boundary conditions
        """
        # Test implementation
        pass

    def test_error_handling(self):
        """Verify proper error handling.

        The system should:
        1. Raise specific exceptions for known error conditions
        2. Include helpful error messages
        3. Clean up resources on failure
        """
        with pytest.raises(ValueError) as exc:
            # Test implementation that raises ValueError
            raise ValueError("Expected error message")
        assert str(exc.value) == "Expected error message"


class TestRelatedFeature:
    """Tests for related functionality that shares setup/context.

    This group focuses on feature Y which interacts with X.
    Tests verify the integration points work correctly.
    """

    def test_interaction(self):
        """Verify features X and Y work together correctly."""
        pass
