"""Module for GitHub operations."""

import sys
from pathlib import Path
import dotenv
from datetime import datetime
from anthropic.types import ToolUseBlock
from github import Github
import os
import shutil
from git import Repo
from src.get_file_list import get_file_list

# Conditional path adjustment before any other imports
if __name__ == "__main__":
    # Calculate path to project root
    project_root = Path(__file__).parent.parent.parent.parent.parent
    sys.path.insert(0, str(project_root))

from src.task.setup import setup_client

dotenv.load_dotenv()

PROMPTS = {
    "system_prompt": (
        "You are an expert code reviewer. Your task is to review pull requests and determine if they meet "
        "requirements. For each PR:\n"
        "1. Examine the changes in the files provided\n"
        "2. Verify each requirement is met\n"
        "3. Run the tests and check they pass\n"
        "4. Write a detailed report with your findings\n"
        "5. Make a clear recommendation (approve/revise/reject)\n\n"
        "Your report should include:\n"
        "- Summary of changes\n"
        "- Requirements check (met/not met for each)\n"
        "- Test results\n"
        "- Recommendation with justification"
    ),
    "review_pr": (
        "Review pull request #{pr_number} in repository {repo}.\n\n"
        "The PR code has been checked out to {repo_path}. The following files are available:\n"
        "{files_list}\n\n"
        "Requirements to check:\n"
        "{requirements}\n\n"
        "Review criteria:\n"
        "- APPROVE if all requirements are met and tests pass\n"
        "- REVISE if there are minor issues: {minor_issues}\n"
        "- REJECT if there are major issues: {major_issues}\n\n"
        "Follow these steps:\n"
        "1. Use read_file to examine changed files\n"
        "2. Use run_tests to verify functionality\n"
        "3. Use comment_on_pr to post your report"
    ),
}


def handle_tool_response(client, response):
    """
    Handle tool responses until natural completion.
    """
    print("Start Conversation")

    while response.stop_reason == "tool_use":
        # Process all tool uses in the current response
        for tool_use in [b for b in response.content if isinstance(b, ToolUseBlock)]:
            print(f"Processing tool: {tool_use.name}")
            print(f"Tool input: {tool_use.input}")
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Execute the tool
            tool_output = client.execute_tool(tool_use)
            print(f"Tool output: {tool_output}")

            # Send tool result back to AI
            response = client.send_message(
                tool_response=str(tool_output),
                tool_use_id=tool_use.id,
                conversation_id=response.conversation_id,
            )
            print(f"Response: {response}")

    print("End Conversation")


def setup_pr_repository(
    repo_owner: str, repo_name: str, pr_number: int
) -> tuple[str, list[str]]:
    """
    Set up a local repository with the PR code checked out.

    Args:
        repo_owner: Owner of the repository
        repo_name: Name of the repository
        pr_number: Pull request number to check out

    Returns:
        tuple[str, list[str]]: Tuple containing:
            - Path to the repository
            - List of files in the repository
    """
    # Generate sequential repo path
    base_dir = os.path.abspath("./repos")
    os.makedirs(base_dir, exist_ok=True)

    # Find first available number
    counter = 0
    while True:
        candidate_path = os.path.join(base_dir, f"repo_{counter}")
        if not os.path.exists(candidate_path):
            repo_path = candidate_path
            break
        counter += 1

    try:
        # Clean existing repository (in case of partial failures)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)

        # Create parent directory
        os.makedirs(os.path.dirname(repo_path), exist_ok=True)

        # Clone repository
        gh = Github(os.getenv("GITHUB_TOKEN"))
        repo = gh.get_repo(f"{repo_owner}/{repo_name}")

        print(f"Cloning repository to {repo_path}")
        git_repo = Repo.clone_from(repo.clone_url, repo_path)

        # Fetch PR
        print(f"Fetching PR #{pr_number}")
        git_repo.remote().fetch(f"pull/{pr_number}/head:pr_{pr_number}")

        # Checkout PR branch
        print("Checking out PR branch")
        git_repo.git.checkout(f"pr_{pr_number}")

        # Get list of files
        files = get_file_list(repo_path)
        print(f"Found {len(files)} files")

        return repo_path, files

    except Exception as e:
        print(f"Error setting up PR repository: {str(e)}")
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        raise


def review_pull_request(
    client,
    repo_owner,
    repo_name,
    pr_number,
    requirements,
    minor_issues,
    major_issues,
):
    """
    Review a specific pull request.

    Args:
        client: The AnthropicClient instance
        repo_owner: Owner of the repository
        repo_name: Name of the repository
        pr_number: Number of the pull request to review
        requirements: List of requirements that PRs must meet
        minor_issues: Description of what constitutes minor issues (leads to REVISE)
        major_issues: Description of what constitutes major issues (leads to REJECT)
    """
    repo_path = None
    try:
        # Set up repository
        repo_path, files = setup_pr_repository(repo_owner, repo_name, pr_number)

        # Create new conversation
        conversation_id = client.create_conversation(
            system_prompt=PROMPTS["system_prompt"],
        )

        # Format requirements as bullet points
        formatted_reqs = "\n".join(f"- {req}" for req in requirements)

        # Format files list
        files_list = "\n".join(f"- {f}" for f in files)

        # Send review prompt
        review_prompt = PROMPTS["review_pr"].format(
            pr_number=pr_number,
            repo=f"{repo_owner}/{repo_name}",
            repo_path=repo_path,
            files_list=files_list,
            requirements=formatted_reqs,
            minor_issues=minor_issues,
            major_issues=major_issues,
        )

        response = client.send_message(
            prompt=review_prompt, conversation_id=conversation_id
        )

        print(f"Response: {response}")

        # Handle tool responses (read files, run tests, comment)
        handle_tool_response(client, response)

    except Exception as e:
        print(f"Error reviewing PR #{pr_number}: {str(e)}")
        raise
    finally:
        # Clean up repository
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)


def review_all_pull_requests(
    repo_owner, repo_name, requirements, minor_issues, major_issues
):
    """
    Review all open pull requests in the specified repository.
    """
    # Set up clients
    gh = Github(os.getenv("GITHUB_TOKEN"))
    client = setup_client()
    repo = gh.get_repo(f"{repo_owner}/{repo_name}")

    # Get all open PRs
    open_prs = repo.get_pulls(state="open")
    print(f"Found {open_prs.totalCount} open pull requests")

    # Review each PR
    for pr in open_prs:
        try:
            print(f"\nReviewing PR #{pr.number}: {pr.title}")
            review_pull_request(
                client=client,
                repo_owner=repo_owner,
                repo_name=repo_name,
                pr_number=pr.number,
                requirements=requirements,
                minor_issues=minor_issues,
                major_issues=major_issues,
            )

        except Exception as e:
            print(f"Error reviewing PR #{pr.number}: {str(e)}")
            continue  # Continue with next PR even if one fails


if __name__ == "__main__":
    # Example usage
    requirements = [
        "Implementation matches problem description",
        "All tests pass",
        "Implementation is in a single file in the /src directory",
        "tests are in a single file in the /tests directory",
        "No other files are modified",
    ]

    minor_issues = (
        "test coverage could be improved but core functionality is tested",
        "implementation and tests exist but are not in the /src and /tests directories",
        "other files are modified",
    )

    major_issues = (
        "Incorrect implementation, failing tests, missing critical features, "
        "no error handling, security vulnerabilities, no tests"
    )

    review_all_pull_requests(
        repo_owner="koii-network",
        repo_name="builder-test",
        requirements=requirements,
        minor_issues=minor_issues,
        major_issues=major_issues,
    )
