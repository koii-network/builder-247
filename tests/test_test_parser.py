"""Tests for the test_parser module."""

import os
import pytest
from dotenv import load_dotenv
from src.test_parser import (
    parse_test_output,
    get_structured_test_data,
    send_test_data_to_claude,
)


@pytest.fixture(autouse=True)
def setup_environment():
    """Set up environment variables before each test."""
    load_dotenv()
    if not os.environ.get("CLAUDE_API_KEY"):
        pytest.skip("CLAUDE_API_KEY environment variable not set")
    yield


def test_parse_test_output():
    """Test that we can correctly parse pytest output."""
    sample_output = """============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
rootdir: /home/user/project
plugins: hypothesis-6.75.3, cov-4.1.0, reportlog-0.3.0, timeout-2.1.0
collected 1 item

test_example.py::test_something FAILED                                      [100%]

=================================== FAILURES ===================================
_______________________________ test_something ________________________________

    def test_something():
>       assert False
E       assert False

test_example.py:2: AssertionError
=========================== short test summary info ============================
FAILED test_example.py::test_something - assert False
============================== 1 failed in 0.05s =============================="""

    result = parse_test_output(sample_output)

    assert isinstance(result, dict)
    assert result["test_name"] == "test_something"
    assert result["test_file"] == "test_example.py"
    assert "assert False" in result["error_message"]
    assert result["full_output"] == sample_output


def test_get_structured_test_data(tmp_path):
    """Test that we can run a test and get structured data about its failure."""
    # Create a failing test file
    test_file = tmp_path / "test_example.py"
    test_file.write_text(
        """
def test_something():
    assert False
"""
    )

    result = get_structured_test_data(f"pytest {test_file} -v")

    assert isinstance(result, dict)
    assert result["test_name"] == "test_something"
    assert str(test_file.name) in result["test_file"]
    assert "assert False" in result["error_message"]
    assert isinstance(result["full_output"], str)


def test_send_test_data_to_claude():
    """Test that we can send test data to Claude and get a structured response."""
    test_data = {
        "test_name": "test_something",
        "test_file": "test_example.py",
        "error_message": "assert False",
        "full_output": "FAILED test_example.py::test_something - assert False",
    }

    response = send_test_data_to_claude(test_data)

    assert isinstance(response, dict)
    assert "test_name" in response
    assert "test_file" in response
    assert "error_message" in response
    assert "full_output" in response
    assert response["test_name"] == "test_something"
    assert response["test_file"] == "test_example.py"
    assert "assert False" in response["error_message"]


def test_send_test_data_to_claude_no_api_key():
    """Test that appropriate error is raised when API key is missing."""
    original_key = os.environ.get("CLAUDE_API_KEY")

    try:
        if "CLAUDE_API_KEY" in os.environ:
            del os.environ["CLAUDE_API_KEY"]

        with pytest.raises(ValueError, match="CLAUDE_API_KEY must be set in .env file"):
            send_test_data_to_claude({})
    finally:
        if original_key is not None:
            os.environ["CLAUDE_API_KEY"] = original_key
