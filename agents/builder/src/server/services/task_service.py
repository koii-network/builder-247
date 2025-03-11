"""Task service module."""

import requests
import os
from flask import jsonify
from github import Github as gh
from src.database import get_db, Submission
from src.clients import setup_client
from src.workflows.utils import setup_repository
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.mergeconflict.workflow import LocalMergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS as CONFLICT_PROMPTS
from src.workflows.task.prompts import PROMPTS as TASK_PROMPTS
from src.utils.logging import logger, log_error, log_section, log_key_value
from dotenv import load_dotenv

load_dotenv()


def complete_todo(task_id, round_number, signature, staking_key, pub_key):
    """Handle task creation request."""
    todo = get_todo(signature, staking_key, pub_key)
    if not todo:
        return jsonify({"error": "No todo found"}), 404

    pr_url = run_todo_task(task_id=task_id, round_number=round_number, todo=todo)

    return jsonify({"roundNumber": round_number, "prUrl": pr_url})


def get_todo(signature, staking_key, pub_key):
    """Get todo from middle server."""
    try:
        logger.info("Fetching todo")

        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + "/api/fetch-to-do",
            json={
                "signature": signature,
                "stakingKey": staking_key,
                "pubKey": pub_key,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Fetch todo response: {result}")

        if result["success"]:
            return result["data"]
        else:
            log_error(
                Exception(result.get("message", "Unknown error")),
                context="Failed to fetch todo",
            )
            return None

    except requests.exceptions.RequestException as e:
        log_error(e, context="Error fetching todo")
        return None


def run_todo_task(task_id, round_number, todo):
    """Run todo task and create PR."""
    try:
        db = get_db()

        # Create new submission
        submission = Submission(
            task_id=task_id,
            round_number=round_number,
            status="running",
            repo_owner=todo["repo_owner"],
            repo_name=todo["repo_name"],
        )
        db.add(submission)
        db.commit()

        # Set up client and workflow
        client = setup_client("anthropic")
        workflow = TaskWorkflow(
            client=client,
            prompts=TASK_PROMPTS,
            repo_owner=todo["repo_owner"],
            repo_name=todo["repo_name"],
            todo=todo["title"],
            acceptance_criteria=todo["acceptance_criteria"],
            round_number=round_number,
            task_id=task_id,
        )

        # Run workflow and get PR URL
        pr_url = workflow.run()
        return pr_url

    except Exception as e:
        log_error(e, context="PR creation failed")
        if "db" in locals():
            # Update submission status
            submission = (
                db.query(Submission)
                .filter(Submission.round_number == round_number)
                .first()
            )
            if submission:
                submission.status = "failed"
                db.commit()
                logger.info(f"Updated status to failed for round {round_number}")
        raise


def record_pr(signature, staking_key, pub_key, pr_url, round_number):
    """Submit PR to middle server and update submission."""
    try:
        db = get_db()
        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + "/api/add-pr-to-to-do",
            json={
                "signature": signature,
                "stakingKey": staking_key,
                "pubKey": pub_key,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        username = os.environ["GITHUB_USERNAME"]

        # Update submission
        submission = (
            db.query(Submission).filter(Submission.round_number == round_number).first()
        )
        if submission:
            submission.status = "completed"
            submission.pr_url = pr_url
            submission.username = username
            db.commit()
            logger.info("Database updated successfully")
            return "PR submitted successfully"
        else:
            log_error(
                Exception("Submission not found"),
                context=f"No submission found for round {round_number}",
            )
            return "Error: Submission not found"

    except requests.exceptions.RequestException as e:
        log_error(e, context="Error submitting PR")
        return "Error submitting PR"


def consolidate_prs(task_id, round_number, signature, staking_key, pub_key):
    """Consolidate PRs from workers."""

    source_repo = fetch_source_repo(task_id)
    repo_url = source_repo["repo_url"]
    repo_owner = source_repo["repo_owner"]
    repo_name = source_repo["repo_name"]
    branch = f"round-{round_number}-{task_id}"

    # Initialize Claude client
    client = setup_client("anthropic")

    source_fork = gh.get_repo(f"{repo_owner}/{repo_name}")

    if not source_fork.fork:
        raise Exception("Source repository is not a fork")

    upstream_repo = source_fork.parent
    print(f"Found upstream repository: {upstream_repo.html_url}")
    setup_result = setup_repository(
        repo_url, github_token=os.environ["MERGE_GITHUB_TOKEN"]
    )
    if not setup_result["success"]:
        raise Exception(
            f"Error setting up repository: {setup_result.get('message', 'Unknown error')}"
        )

    our_fork_url = setup_result["data"]["fork_url"]
    print(f"Using fork: {our_fork_url}")

    open_prs = list(source_fork.get_pulls(state="open", base=branch))
    # Sort PRs by creation date (oldest first)
    open_prs.sort(key=lambda pr: pr.created_at)
    print(f"\nFound {len(open_prs)} open PRs to process")
    merged_prs = []
    failed_prs = []

    for pr in open_prs:
        # Use the workflow to process all PRs with the limit
        workflow = LocalMergeConflictWorkflow(
            client=client,
            prompts=CONFLICT_PROMPTS,
            repo_url=repo_url,
            target_branch=branch,
            pr_url=pr.html_url,
        )

        result = workflow.run()

        if result and result["success"]:
            merged_prs.append(pr.number)
        else:
            failed_prs.append(pr.number)

    log_section("Merge summary")
    log_key_value("Total PRs processed", len(open_prs))
    log_key_value("Successfully merged", len(merged_prs))
    log_key_value("Failed to merge", len(failed_prs))


def create_aggregator_repo(round_number, task_id):
    """Create an aggregator repo for a given round and task.

    Args:
        round_number (int): The round number
        task_id (str): The task ID

    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the operation succeeded
            - message (str): Success/error message
            - data (dict): Contains fork_url and branch_name if successful
    """
    try:
        # Get source repo info
        source_repo = fetch_source_repo(task_id)
        repo_owner = source_repo["repo_owner"]
        repo_name = source_repo["repo_name"]

        # Initialize GitHub client with token
        github = gh(os.environ["GITHUB_TOKEN"])
        username = os.environ["GITHUB_USERNAME"]

        # Check if fork already exists
        try:
            fork = github.get_repo(f"{username}/{repo_name}")
            log_key_value("Using existing fork", fork.html_url)
        except Exception:
            # Create new fork if it doesn't exist
            source = github.get_repo(f"{repo_owner}/{repo_name}")
            fork = github.get_user().create_fork(source)
            log_key_value("Created new fork", fork.html_url)

        # Create branch name
        branch_name = f"round-{round_number}-{task_id}"

        try:
            # Get the default branch's SHA
            default_branch = fork.default_branch
            default_branch_sha = fork.get_branch(default_branch).commit.sha

            # Create branch if it doesn't exist
            fork.create_git_ref(f"refs/heads/{branch_name}", default_branch_sha)
            log_key_value("Created new branch", branch_name)

            return {
                "success": True,
                "message": "Successfully created aggregator repository",
                "data": {"fork_url": fork.html_url, "branch_name": branch_name},
            }

        except Exception as e:
            log_error(e, "Failed to create branch")
            return {
                "success": False,
                "message": f"Failed to create branch: {str(e)}",
                "data": None,
            }

    except Exception as e:
        log_error(e, "Failed to create aggregator repository")
        return {
            "success": False,
            "message": f"Failed to create aggregator repository: {str(e)}",
            "data": None,
        }


def fetch_source_repo(task_id):
    """Fetch the source repo for a given task."""
    response = requests.post(
        os.environ["MIDDLE_SERVER_URL"] + "/api/source-repo",
        json={
            "taskId": task_id,
        },
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response.json()
