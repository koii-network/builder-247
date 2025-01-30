"""Integration tests for GitHub operations tools."""

import os
import pytest
import time
from dotenv import load_dotenv
from src.anthropic_client import AnthropicClient
from anthropic.types import Message

# Load environment variables before any tests
load_dotenv()


@pytest.fixture(autouse=True)
def setup_environment(tmp_path):
    """Set up environment variables and client before each test."""
    if not os.environ.get("GITHUB_TOKEN"):
        pytest.skip("GITHUB_TOKEN environment variable not set")
    api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        pytest.skip("CLAUDE_API_KEY environment variable not set")
    temp_db = tmp_path / "test.db"
    client = AnthropicClient(api_key=api_key, db_path=temp_db)
    client.register_tools_from_directory("src/tools/definitions/github_operations")
    return client


def handle_tool_response(client, response, conversation_id=None, max_iterations=5):
    """
    Handle tool responses recursively until we get a text response.

    Args:
        client: The AnthropicClient instance
        response: The current response from Claude
        conversation_id: The conversation ID for continuity
        max_iterations: Maximum number of tool calls to handle

    Returns:
        The final text response from Claude
    """
    iterations = 0
    while response.stop_reason == "tool_use" and iterations < max_iterations:
        iterations += 1
        tool_use = next(block for block in response.content if block.type == "tool_use")
        result = client.execute_tool(tool_use)

        # Format the tool response based on the tool type
        if tool_use.name == "create_pull_request":
            tool_response = result["pr_url"] if result["success"] else result["error"]
        elif tool_use.name == "get_pr_template":
            tool_response = result["template"] if result["success"] else result["error"]
        elif tool_use.name == "check_fork_exists":
            tool_response = "exists" if result["exists"] else "does not exist"
        else:
            tool_response = "success" if result["success"] else result["error"]

        response = client.send_message(
            tool_response=tool_response,
            tool_use_id=tool_use.id,
            conversation_id=conversation_id,
        )

    return response


def test_check_fork_exists(setup_environment):
    """Test the check_fork_exists tool."""
    client = setup_environment

    # 1. Initial prompt to Claude
    message = client.send_message(
        "Can you check if the repository torvalds/linux exists on GitHub?",
        tool_choice={"type": "any"},
    )

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "check_fork_exists"

    # 3. Execute tool and handle response
    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="exists" if result["exists"] else "does not exist",
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Handle any additional tool calls and verify final response
    response = handle_tool_response(client, response, message.conversation_id)
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert "exists" in response.content[0].text.lower()

    time.sleep(2)  # Rate limiting


def test_fork_repository(setup_environment):
    """Test the fork_repository tool."""
    client = setup_environment

    # 1. Initial prompt to Claude
    message = client.send_message(
        "Can you fork the hello-world repository from octocat?",
        tool_choice={"type": "any"},
    )

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "fork_repository"

    # 3. Execute tool and handle response
    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Handle any additional tool calls and verify final response
    response = handle_tool_response(client, response, message.conversation_id)
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert "success" in response.content[0].text.lower()

    time.sleep(2)  # Rate limiting


def test_create_pull_request(setup_environment):
    """Test the create_pull_request tool."""
    client = setup_environment

    # 1. Initial prompt to Claude
    message = client.send_message(
        "Can you create a pull request in the octocat/hello-world repository "
        "with the title 'Test PR' and description 'This is a test PR'?",
        tool_choice={"type": "any"},
    )

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")

    # 3. Execute tool and handle response
    result = client.execute_tool(tool_use)
    if tool_use.name == "create_pull_request":
        tool_response = result["pr_url"] if result["success"] else result["error"]
    elif tool_use.name == "get_pr_template":
        tool_response = result["template"] if result["success"] else result["error"]
    else:
        tool_response = "success" if result["success"] else result["error"]

    response = client.send_message(
        tool_response=tool_response,
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Handle any additional tool calls and verify final response
    response = handle_tool_response(client, response, message.conversation_id)
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert "pull" in response.content[0].text.lower()

    time.sleep(2)  # Rate limiting


def test_get_pr_template(setup_environment):
    """Test the get_pr_template tool."""
    client = setup_environment

    # 1. Initial prompt to Claude
    message = client.send_message(
        "Can you get the PR template for this repository?",
        tool_choice={"type": "any"},
    )

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "get_pr_template"

    # 3. Execute tool and handle response
    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response=result["template"] if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Handle any additional tool calls and verify final response
    response = handle_tool_response(client, response, message.conversation_id)
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert "template" in response.content[0].text.lower()

    time.sleep(2)  # Rate limiting


def test_sync_fork(setup_environment):
    """Test the sync_fork tool."""
    client = setup_environment

    # 1. Initial prompt to Claude
    message = client.send_message(
        "Can you sync my fork of the hello-world repository with the upstream repository?",
        tool_choice={"type": "any"},
    )

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "sync_fork"

    # 3. Execute tool and handle response
    result = client.execute_tool(tool_use)
    response = client.send_message(
        tool_response="success" if result["success"] else result["error"],
        tool_use_id=tool_use.id,
        conversation_id=message.conversation_id,
    )

    # 4. Handle any additional tool calls and verify final response
    response = handle_tool_response(client, response, message.conversation_id)
    assert isinstance(response, Message)
    assert all(block.type == "text" for block in response.content)
    assert "sync" in response.content[0].text.lower()

    time.sleep(2)  # Rate limiting
