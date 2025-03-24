"""Task service module."""

import requests
import os
from github import Github
from src.database import get_db, Submission
from src.clients import setup_client
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.mergeconflict.workflow import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS as CONFLICT_PROMPTS
from src.workflows.task.prompts import PROMPTS as TASK_PROMPTS
from src.utils.logging import logger, log_error, log_key_value
from src.workflows.utils import verify_pr_signatures
from src.utils.distribution import validate_distribution_list
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
        github = Github(os.environ["GITHUB_TOKEN"])
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


def _check_existing_pr(round_number: int, task_id: str) -> dict:
    """Check if we already have a completed record for this round."""
    try:
        db = get_db()
        submission = (
            db.query(Submission)
            .filter(
                Submission.round_number == round_number,
                Submission.task_id == task_id,
                Submission.status == "completed",
            )
            .first()
        )

        if submission:
            logger.info(f"PR already recorded for task {task_id}, round {round_number}")
            return {
                "success": True,
                "data": {"message": "PR already recorded", "pr_url": submission.pr_url},
            }
        return {"success": False}
    except Exception as e:
        log_error(e, "Failed to check existing PR")
        return {"success": False, "status": 500, "error": str(e)}


def _store_pr_remotely(
    staking_key: str, staking_signature: str, pub_key: str, pr_url: str
) -> dict:
    """Store PR URL in middle server."""
    try:
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
        return {
            "success": True,
            "data": {"message": "PR recorded remotely", "pr_url": pr_url},
        }
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


def _store_pr_locally(round_number: int, pr_url: str, task_id: str) -> dict:
    """Store PR URL in local database."""
    try:
        db = get_db()
        username = os.environ["GITHUB_USERNAME"]

        # Update submission status
        submission = (
            db.query(Submission)
            .filter(
                Submission.round_number == round_number,
                Submission.task_id == task_id,
            )
            .first()
        )
        if submission:
            submission.status = "completed"
            if not submission.pr_url:  # Only update PR URL if not already set
                submission.pr_url = pr_url
            submission.username = username
            db.commit()
            logger.info("Local database updated successfully")
            return {
                "success": True,
                "data": {"message": "PR recorded locally", "pr_url": pr_url},
            }
        else:
            error_msg = f"No submission found for task {task_id}, round {round_number}"
            log_error(
                Exception("Submission not found"),
                context=error_msg,
            )
            return {"success": False, "status": 404, "error": error_msg}
    except Exception as e:
        log_error(e, "Failed to store PR locally")
        return {"success": False, "status": 500, "error": str(e)}


def record_pr(
    staking_key,
    staking_signature,
    pub_key,
    pr_url,
    round_number,
    task_id,
    node_type="worker",
):
    """Record PR URL locally and optionally remotely.

    Args:
        staking_key: Node's staking key
        staking_signature: Node's signature
        pub_key: Node's public key
        pr_url: URL of the PR to record
        round_number: Round number
        task_id: Task ID
        node_type: Type of node ("worker" or "leader"). Workers record both locally and remotely.
    """
    # First check if we already have a record
    existing = _check_existing_pr(round_number, task_id)
    if existing["success"]:
        return existing

    # For workers, record with middle server first as it's the source of truth
    if node_type == "worker":
        remote_result = _store_pr_remotely(
            staking_key, staking_signature, pub_key, pr_url
        )
        if not remote_result["success"]:
            return remote_result

    # Only record locally after successful remote recording (for workers)
    # or immediately (for leaders)
    local_result = _store_pr_locally(round_number, pr_url, task_id)
    if not local_result["success"]:
        return local_result

    return {
        "success": True,
        "data": {"message": "PR recorded successfully", "pr_url": pr_url},
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
    """Consolidate PRs from workers."""
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

        # Get source fork
        github = Github(os.environ["GITHUB_TOKEN"])
        source_fork = github.get_repo(f"{os.environ['GITHUB_USERNAME']}/{repo_name}")

        # Verify this is a fork
        if not source_fork.fork:
            submission.status = "failed"
            db.commit()
            return {
                "success": False,
                "status": 400,
                "error": "Source repository is not a fork",
            }

        upstream_repo = source_fork.parent
        print(f"Found upstream repository: {upstream_repo.html_url}")

        # Validate and filter distribution list
        filtered_distribution_list, error = validate_distribution_list(
            distribution_list, repo_owner, repo_name
        )
        if error:
            submission.status = "failed"
            db.commit()
            return {
                "success": False,
                "status": 400,
                "error": error,
            }

        # Get list of open PRs
        branch = f"task-{task_id}-round-{round_number - 3}"
        open_prs = list(source_fork.get_pulls(state="open", base=branch))
        print(f"\nFound {len(open_prs)} open PRs")
        print("Open PRs:")
        for pr in open_prs:
            print(f"  #{pr.number}: {pr.title} by {pr.user.login}")

        # Filter PRs based on signature validation
        valid_prs = []
        for pr in open_prs:
            # For each PR, try to find a valid signature from a rewarded staking key
            print(f"\nChecking PR #{pr.number} against staking keys:")
            for submitter_key in filtered_distribution_list:
                print(f"  Checking staking key: {submitter_key}")
                is_valid = verify_pr_signatures(
                    pr.body,
                    task_id,
                    round_number - 3,
                    expected_staking_key=submitter_key,
                )
                if is_valid:
                    valid_prs.append(pr)
                    print(f"  ✓ Found valid signature for {submitter_key}")
                    break
                else:
                    print(f"  ✗ No valid signature for {submitter_key}")

        print(f"\nFound {len(valid_prs)} PRs with valid signatures")

        if not valid_prs:
            print("No valid PRs to consolidate")
            submission.status = "failed"
            db.commit()
            return {
                "success": False,
                "status": 400,
                "error": "No PRs with valid signatures found",
            }

        # Create workflow instance with validated PRs
        print("\nCreating workflow with:")
        print(f"  task_id: {task_id}")
        print(f"  round_number: {round_number}")
        print(f"  staking_keys: {list(filtered_distribution_list.keys())}")

        # Initialize Claude client
        client = setup_client("anthropic")

        workflow = MergeConflictWorkflow(
            client=client,
            prompts=CONFLICT_PROMPTS,
            source_fork_url=source_fork.html_url,
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
        if not pr_url:
            log_error(
                Exception("No PR URL returned from workflow"),
                context="Merge workflow failed to create PR",
            )
            submission.status = "failed"
            db.commit()
            return {
                "success": False,
                "status": 500,
                "error": "Merge workflow failed to create PR",
            }

        # Store PR URL in local DB immediately
        submission.pr_url = pr_url
        submission.status = "pending_record"  # New status to indicate PR exists but not recorded with middle server
        db.commit()
        logger.info(
            f"Stored PR URL {pr_url} locally for task {task_id}, round {round_number}"
        )

        return {
            "success": True,
            "data": {"pr_url": pr_url, "message": "PRs consolidated successfully"},
        }

    except Exception as e:
        log_error(e, context="PR consolidation failed")
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


def create_aggregator_repo(issue_id, repo_owner, repo_name):
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
        github = Github(os.environ["GITHUB_TOKEN"])
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

        branch_name = issue_id

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


def assign_issue(task_id):
    try:

        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + "/api/assign-issue",
            json={"taskId": task_id},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        result = response.json()

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
