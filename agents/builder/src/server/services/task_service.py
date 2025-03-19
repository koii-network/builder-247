"""Task service module."""

import requests
import os
from github import Github as gh
from src.database import get_db, Submission
from src.clients import setup_client
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.mergeconflict.workflow import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS as CONFLICT_PROMPTS
from src.workflows.task.prompts import PROMPTS as TASK_PROMPTS
from src.utils.logging import logger, log_error, log_key_value
from src.workflows.utils import verify_pr_signatures
from src.utils.filter_distribution import remove_leaders
from dotenv import load_dotenv

load_dotenv()


def complete_todo(
    task_id,
    round_number,
    staking_key,
    staking_signature,
    pub_key,
    public_signature,
    repo_owner,
    repo_name,
    **kwargs,
):
    """Handle task creation request."""
    try:
        # Check if base branch exists in target repo
        github = gh(os.environ["GITHUB_TOKEN"])
        target_repo = github.get_repo(f"{repo_owner}/{repo_name}")
        base_branch = f"task-{task_id}-round-{round_number}"

        try:
            target_repo.get_branch(base_branch)
        except Exception:
            return {
                "success": False,
                "status": 400,
                "error": (
                    f"Base branch '{base_branch}' does not exist in target repository."
                ),
            }

        # Proceed with todo request
        todo_result = get_todo(staking_signature, staking_key, pub_key)
        if not todo_result.get("success", False):
            return {
                "success": False,
                "status": todo_result.get("status", 500),
                "error": todo_result.get("error", "Unknown error fetching todo"),
            }
        todo = todo_result["data"]

        try:
            result = run_todo_task(
                task_id=task_id,
                round_number=round_number,
                todo=todo,
                staking_key=staking_key,
                pub_key=pub_key,
                staking_signature=staking_signature,
                public_signature=public_signature,
                repo_owner=repo_owner,
                repo_name=repo_name,
            )

            if not result.get("success", False):
                return result

            return {
                "success": True,
                "data": {
                    "pr_url": result["data"]["pr_url"],
                    "message": result["data"]["message"],
                },
            }
        except Exception as e:
            return {"success": False, "status": 500, "error": str(e)}
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "error": f"Failed to check base branch: {str(e)}",
        }


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

        if not result.get("success", False):
            return {
                "success": False,
                "status": 400,
                "error": result.get("message", "Unknown error from middle server"),
            }

        return {"success": True, "data": result.get("data", {})}

    except requests.exceptions.RequestException as e:
        if not hasattr(e, "response") or e.response is None:
            return {
                "success": False,
                "status": 500,
                "error": "No response from middle server",
            }

        # Parse the JSON error response
        try:
            error_data = e.response.json()
            error_message = error_data.get("message", "Unknown error")
        except ValueError:
            error_message = e.response.text

        return {
            "success": False,
            "status": e.response.status_code,
            "error": error_message,  # Use parsed message instead of raw JSON
        }


def run_todo_task(
    task_id,
    round_number,
    todo,
    staking_key,
    pub_key,
    staking_signature,
    public_signature,
    repo_owner,
    repo_name,
):
    """Run todo task and create PR."""
    try:
        db = get_db()

        # Check if we already have a PR URL for this submission
        existing_submission = (
            db.query(Submission)
            .filter(
                Submission.task_id == task_id, Submission.round_number == round_number
            )
            .first()
        )

        if existing_submission and existing_submission.pr_url:
            logger.info(
                f"Found existing PR URL for task {task_id}, round {round_number}"
            )
            return {
                "success": True,
                "data": {
                    "pr_url": existing_submission.pr_url,
                    "message": "Using existing PR URL",
                },
            }

        # If no existing submission with PR URL, delete any incomplete submission
        if existing_submission:
            db.delete(existing_submission)
            db.commit()
            logger.info(
                f"Deleted existing incomplete submission for task {task_id}, round {round_number}"
            )

        # Create new submission
        submission = Submission(
            task_id=task_id,
            round_number=round_number,
            status="running",
            repo_owner=repo_owner,
            repo_name=repo_name,
        )
        db.add(submission)
        db.commit()

        # Set up client and workflow
        client = setup_client("anthropic")
        workflow = TaskWorkflow(
            client=client,
            prompts=TASK_PROMPTS,
            repo_owner=repo_owner,
            repo_name=repo_name,
            todo=todo["title"],
            acceptance_criteria=todo["acceptance_criteria"],
            round_number=round_number,
            task_id=task_id,
            staking_key=staking_key,
            pub_key=pub_key,
            staking_signature=staking_signature,
            public_signature=public_signature,
            base_branch=f"task-{task_id}-round-{round_number}",
        )

        # Run workflow and get PR URL
        pr_url = workflow.run()

        # Store PR URL in local DB immediately
        submission.pr_url = pr_url
        submission.status = "pending_record"  # New status to indicate PR exists but not recorded with middle server
        db.commit()
        logger.info(
            f"Stored PR URL {pr_url} locally for task {task_id}, round {round_number}"
        )

        return {
            "success": True,
            "data": {"pr_url": pr_url, "message": "Created new PR"},
        }

    except Exception as e:
        log_error(e, context="PR creation failed")
        if "db" in locals():
            # Update submission status
            submission = (
                db.query(Submission)
                .filter(
                    Submission.task_id == task_id,
                    Submission.round_number == round_number,
                )
                .first()
            )
            if submission:
                submission.status = "failed"
                db.commit()
                logger.info(
                    f"Updated status to failed for task {task_id}, round {round_number}"
                )
        return {"success": False, "status": 500, "error": str(e)}


def record_pr(staking_key, staking_signature, pub_key, pr_url, round_number):
    """Submit PR to middle server and update submission."""
    try:
        db = get_db()

        # First check if we already have a completed record
        submission = (
            db.query(Submission)
            .filter(
                Submission.round_number == round_number,
                Submission.status == "completed",
            )
            .first()
        )

        if submission:
            logger.info(f"PR already recorded for round {round_number}")
            return {
                "success": True,
                "data": {"message": "PR already recorded", "pr_url": submission.pr_url},
            }

        # Try to record with middle server
        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + "/api/add-pr-to-to-do",
            json={
                "signature": staking_signature,
                "stakingKey": staking_key,
                "pubKey": pub_key,
                "prUrl": pr_url,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        username = os.environ["GITHUB_USERNAME"]

        # Update submission status after successful middle server record
        submission = (
            db.query(Submission).filter(Submission.round_number == round_number).first()
        )
        if submission:
            submission.status = "completed"
            if not submission.pr_url:  # Only update PR URL if not already set
                submission.pr_url = pr_url
            submission.username = username
            db.commit()
            logger.info("Database updated successfully")
            return {
                "success": True,
                "data": {"message": "PR submitted successfully", "pr_url": pr_url},
            }
        else:
            error_msg = f"No submission found for round {round_number}"
            log_error(
                Exception("Submission not found"),
                context=error_msg,
            )
            return {"success": False, "status": 404, "error": error_msg}

    except requests.exceptions.RequestException as e:
        if not hasattr(e, "response"):
            return {
                "success": False,
                "status": 500,
                "error": "No response from middle server",
            }
        return {
            "success": False,
            "status": e.response.status_code,
            "error": e.response.text,
        }


def consolidate_prs(
    task_id,
    round_number,
    distribution_list,
    staking_key,
    pub_key,
    staking_signature,
    public_signature,
    repo_owner,
    repo_name,
):
    """Consolidate PRs from workers.

    Args:
        task_id (str): The task ID
        round_number (int): The round number
        distribution_list (dict): Dictionary mapping staking keys to amounts
        submitter_staking_key (str): Leader's staking key
        pub_key (str): Leader's public key
        staking_signature (str): Leader's staking signature
        public_signature (str): Leader's public signature
    """
    branch = f"task-{task_id}-round-{round_number - 3}"
    repo_url = f"https://github.com/{repo_owner}/{repo_name}"

    # Initialize Claude client
    client = setup_client("anthropic")

    github = gh(os.environ["GITHUB_TOKEN"])
    source_fork = github.get_repo(f"{repo_owner}/{repo_name}")

    if not source_fork.fork:
        raise Exception("Source repository is not a fork")

    upstream_repo = source_fork.parent
    print(f"Found upstream repository: {upstream_repo.html_url}")

    # Filter out leader PRs from distribution list
    filtered_distribution_list = remove_leaders(
        distribution_list=distribution_list,
        repo_owner=repo_owner,
        repo_name=repo_name,
    )

    if not filtered_distribution_list:
        print("No eligible worker PRs to consolidate after filtering out leader PRs")
        return None

    # Get list of open PRs
    open_prs = list(source_fork.get_pulls(state="open", base=branch))
    print(f"Found {len(open_prs)} open PRs")

    # Filter PRs based on signature validation
    valid_prs = []
    for pr in open_prs:
        # For each PR, try to find a valid signature from a rewarded staking key
        for submitter_key in filtered_distribution_list:
            is_valid = verify_pr_signatures(
                pr.body,
                task_id,
                round_number - 3,
                expected_staking_key=submitter_key,
            )
            if is_valid:
                valid_prs.append(pr)
                break

    print(f"Found {len(valid_prs)} PRs with valid signatures")

    if not valid_prs:
        print("No valid PRs to consolidate")
        return None

    # Create workflow instance with validated PRs
    workflow = MergeConflictWorkflow(
        client=client,
        prompts=CONFLICT_PROMPTS,
        source_fork_url=repo_url,
        source_branch=branch,
        is_source_fork_owner=False,  # We're consolidating PRs from another fork
        staking_key=staking_key,
        pub_key=pub_key,
        staking_signature=staking_signature,
        public_signature=public_signature,
        task_id=task_id,  # Add task_id for signature validation
        round_number=round_number - 3,  # Add round_number for signature validation
        staking_keys=filtered_distribution_list.keys(),  # Use filtered distribution list
    )

    # Run workflow
    pr_url = workflow.run()
    return {
        "success": True,
        "data": {"pr_url": pr_url, "message": "PRs consolidated successfully"},
    }


def create_aggregator_repo(round_number, task_id, repo_owner, repo_name):
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
        # Initialize GitHub client with token
        github = gh(os.environ["GITHUB_TOKEN"])
        username = os.environ["GITHUB_USERNAME"]

        # Get original source repo
        source_repo = github.get_repo(f"{repo_owner}/{repo_name}")
        if source_repo.fork:
            source_repo = source_repo.parent
            repo_owner = source_repo.owner.login
            repo_name = source_repo.name

        # Check if fork already exists
        try:
            fork = github.get_repo(f"{username}/{repo_name}")
            log_key_value("Using existing fork", fork.html_url)
        except Exception:
            # Create new fork if it doesn't exist
            fork = github.get_user().create_fork(source_repo)
            log_key_value("Created new fork", fork.html_url)

        # Create standard aggregator branch name
        branch_name = f"task-{task_id}-round-{round_number}"

        try:
            # Check if branch already exists
            try:
                fork.get_branch(branch_name)
                log_key_value("Using existing branch", branch_name)
                return {
                    "success": True,
                    "message": "Using existing aggregator repository and branch",
                    "data": {"fork_url": fork.html_url, "branch_name": branch_name},
                }
            except Exception:
                # Branch doesn't exist, create it
                default_branch = fork.default_branch
                default_branch_sha = fork.get_branch(default_branch).commit.sha
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


# def fetch_source_repo(task_id):
#     """Fetch the source repo for a given task."""
#     try:
#         response = requests.post(
#             os.environ["MIDDLE_SERVER_URL"] + "/api/source-repo",
#             json={
#                 "taskId": task_id,
#             },
#             headers={"Content-Type": "application/json"},
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         if not hasattr(e, "response"):
#             return {"status": 500, "error": "No response from middle server"}
#         return {"status": e.response.status_code, "error": e.response.text}
