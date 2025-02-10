"""Integration tests for GitHub operations tools."""

import os
import pytest
import time
import tempfile
from dotenv import load_dotenv
from src.anthropic_client import AnthropicClient
from anthropic.types import Message
from src.tools.github_operations import fork_repository
from github import Github, Auth

# Load environment variables before any tests
load_dotenv()


def get_api_key(max_retries=3, retry_delay=1):
    """
    Get API key with retries to handle mounted volume synchronization.

    Args:
        max_retries (int): Maximum number of retries
        retry_delay (int): Delay in seconds between retries
    """
    for attempt in range(max_retries):
        # Try environment variable first
        api_key = os.environ.get("CLAUDE_API_KEY")
        if api_key:
            return api_key

        # Try loading from .env
        load_dotenv()
        api_key = os.environ.get("CLAUDE_API_KEY")
        if api_key:
            return api_key

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    return None


@pytest.fixture(autouse=True)
def setup_environment(tmp_path):
    """Set up environment variables and client before each test."""
    if not os.environ.get("GITHUB_TOKEN"):
        pytest.skip("GITHUB_TOKEN environment variable not set")
    api_key = get_api_key()
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

        # Format the tool response based on the tool type and result
        if not result["success"]:
            tool_response = result.get("error", "Operation failed")
        elif tool_use.name == "create_pull_request":
            tool_response = result["pr_url"]
        elif tool_use.name == "get_pr_template":
            tool_response = result["template"]
        elif tool_use.name == "check_fork_exists":
            tool_response = (
                "exists" if result.get("exists", False) else "does not exist"
            )
        elif tool_use.name == "sync_fork":
            tool_response = "Successfully synced fork"
        else:
            tool_response = "Operation completed successfully"

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


@pytest.fixture
def test_repo():
    """Create a temporary test repository using upstream credentials."""
    upstream_token = os.environ.get("UPSTREAM_GITHUB_TOKEN")
    upstream_username = os.environ.get("UPSTREAM_GITHUB_USERNAME")
    if not upstream_token or not upstream_username:
        pytest.skip("UPSTREAM_GITHUB_TOKEN or UPSTREAM_GITHUB_USERNAME not set")

    # Create a GitHub client with upstream credentials
    gh = Github(auth=Auth.Token(upstream_token))
    user = gh.get_user()

    # Create a temporary test repository
    repo_name = f"test-repo-{int(time.time())}"
    repo = user.create_repo(repo_name, private=False)

    # Add a sample file to the repository
    repo.create_file(
        "README.md",
        "Initial commit",
        "# Test Repository\nThis is a temporary test repository.",
    )
    time.sleep(2)

    yield repo.full_name

    try:
        # Clean up - delete the repository
        repo.delete()
    except Exception as e:
        print(f"Warning: Failed to delete test repository: {e}")


def test_fork_repository(setup_environment, tmp_path, test_repo):
    """Test the fork_repository tool."""
    client = setup_environment
    repo_path = tmp_path / "test-repo"

    # 1. Initial prompt to Claude
    message = client.send_message(
        f"Can you fork the repository {test_repo} into {repo_path}?",
        tool_choice={"type": "any"},
    )

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "fork_repository"
    assert str(repo_path) in str(tool_use.input.get("local_path", ""))

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

    # Verify the repository was cloned to the correct location
    assert repo_path.exists()
    assert (repo_path / ".git").exists()

    time.sleep(2)  # Rate limiting


def test_create_pull_request(setup_environment):
    """Test the create_pull_request tool."""
    client = setup_environment

    # 1. Initial prompt to Claude
    message = client.send_message(
        "Can you create a pull request in the octocat/hello-world repository "
        "with the title 'Test PR' and description 'This is a test PR'? "
        "Please skip template validation for this PR.",
        tool_choice={"type": "any"},
    )

    # 2. Verify Claude's tool selection
    assert isinstance(message, Message)
    assert message.stop_reason == "tool_use"
    tool_use = next(block for block in message.content if block.type == "tool_use")
    assert tool_use.name == "create_pull_request"
    assert tool_use.input.get("validate_template") is False

    # 3. Execute tool and handle response
    result = client.execute_tool(tool_use)
    tool_response = result["pr_url"] if result["success"] else result["error"]

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

    # First fork the repository to ensure we have something to sync
    with tempfile.TemporaryDirectory() as temp_dir:
        # Fork and clone the repository
        fork_result = fork_repository("octocat/hello-world", temp_dir)
        assert fork_result["success"]

        # Wait for GitHub to propagate the fork
        print("Waiting for fork to be initialized...")
        time.sleep(2)

        # 1. Initial prompt to Claude
        message = client.send_message(
            f"Please sync my fork of the hello-world repository in {temp_dir} with its upstream repository.",
            tool_choice={"type": "any"},
        )

        # 2. Verify Claude's tool selection
        assert isinstance(message, Message)
        assert message.stop_reason == "tool_use"
        tool_use = next(block for block in message.content if block.type == "tool_use")
        assert tool_use.name == "sync_fork"
        assert tool_use.input["repo_path"] == temp_dir

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
