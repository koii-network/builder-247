"""Task service module."""

import requests
import os
from github import Github
from src.database import get_db, Submission
from agent_framework.clients import setup_client
from agent_framework.utils.logging import logger, log_error
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.mergeconflict.workflow import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS as CONFLICT_PROMPTS
from src.workflows.task.prompts import PROMPTS as TASK_PROMPTS

from dotenv import load_dotenv

load_dotenv()


def complete_todo(
    task_id,
    round_number,
    staking_key,
    staking_signature,
    pub_key,
    public_signature,
    **kwargs,
):
    """Handle task creation request."""
    try:
        # Proceed with todo request
        todo_result = get_task_details(
            staking_signature, staking_key, pub_key, "worker"
        )
        if not todo_result.get("success", False):
            return {
                "success": False,
                "status": todo_result.get("status", 500),
                "error": todo_result.get("error", "Unknown error fetching todo"),
            }
        todo = todo_result["data"]

        # Use aggregator owner if it was provided
        repo_owner = todo.get("repo_owner")
        repo_name = todo.get("repo_name")
        base_branch = todo.get("issue_uuid")

        # Log what we received from the server
        logger.info(f"Received todo data: {todo}")
        logger.info(
            f"Repository info from todo: owner={repo_owner}, name={repo_name}, branch={base_branch}"
        )

        # Check required fields
        if not repo_owner or not repo_name or not base_branch:
            error_msg = (
                f"Missing required fields in todo data. "
                f"repo_owner={repo_owner}, repo_name={repo_name}, branch={base_branch}"
            )
            return {
                "success": False,
                "status": 400,
                "error": error_msg,
            }

        # Check if base branch exists in target repo
        github = Github(os.environ["GITHUB_TOKEN"])
        try:
            repo_url = f"{repo_owner}/{repo_name}"
            logger.info(f"Attempting to find repository: {repo_url}")
            target_repo = github.get_repo(repo_url)
            logger.info(f"Found target repo: {target_repo.html_url}")
        except Exception as e:
            logger.error(f"Failed to find repository {repo_url}: {str(e)}")
            return {
                "success": False,
                "status": 404,
                "error": f"Repository {repo_owner}/{repo_name} not found: {str(e)}",
            }

        try:
            logger.info(
                f"Checking if branch '{base_branch}' exists in {target_repo.html_url}"
            )
            # Get branch but don't store it since we only need to check if it exists
            target_repo.get_branch(base_branch)
            logger.info(f"Found branch: {base_branch} in {target_repo.html_url}")
        except Exception as e:
            logger.error(
                f"Failed to find branch '{base_branch}' in {target_repo.html_url}: {str(e)}"
            )
            error_msg = (
                f"Base branch '{base_branch}' does not exist in repository "
                f"{repo_owner}/{repo_name} ({target_repo.html_url}): {str(e)}"
            )
            return {
                "success": False,
                "status": 400,
                "error": error_msg,
            }

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
                base_branch=base_branch,
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


def get_task_details(signature, staking_key, pub_key, task_type):
    """Get task details from middle server."""

    tasks_urls = {
        "worker": "/api/fetch-to-do",
        "leader": "/api/fetch-issue",
    }
    try:
        logger.info(f"Fetching {task_type} task")

        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + tasks_urls[task_type],
            json={
                "signature": signature,
                "stakingKey": staking_key,
                "pubKey": pub_key,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Fetch response: {result}")

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
    base_branch,
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

        # Create new submission with issue_uuid and node_type
        submission = Submission(
            task_id=task_id,
            round_number=round_number,
            status="running",
            repo_owner=repo_owner,
            repo_name=repo_name,
            issue_uuid=base_branch,  # Store issue_uuid (base_branch contains it)
            node_type="worker",  # Set node_type to worker
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
            base_branch=base_branch,
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
    """Check if we already have a completed record for this round in local DB.

    Returns the PR URL if found, but doesn't prevent remote recording.
    """
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

        if submission and submission.pr_url:
            logger.info(
                f"Local PR record found for task {task_id}, round {round_number}"
            )
            return {
                "success": True,
                "data": {
                    "message": "Local PR record found",
                    "pr_url": submission.pr_url,
                },
                "skip_local_recording": True,  # Flag to skip local recording but still do remote
            }
        return {"success": False}
    except Exception as e:
        log_error(e, "Failed to check existing PR")
        return {"success": False, "status": 500, "error": str(e)}


def _store_pr_remotely(
    staking_key: str,
    staking_signature: str,
    pub_key: str,
    pr_url: str,
    node_type: str = "worker",
    issue_uuid: str = None,
    task_id: str = None,
    round_number: int = None,
) -> dict:
    """Store PR URL in middle server.

    Uses different endpoints based on node_type:
    - worker: /api/add-pr-to-to-do
    - leader: /api/add-issue-pr

    For leader tasks, the issue_uuid must be included in the request body.
    If issue_uuid is not provided, will attempt to get it from the database using task_id and round_number.
    """
    try:
        # Determine the endpoint based on node type
        endpoint = (
            "/api/add-pr-to-to-do" if node_type == "worker" else "/api/add-issue-pr"
        )

        # Base payload used by both endpoints
        payload = {
            "signature": staking_signature,
            "stakingKey": staking_key,
            "pubKey": pub_key,
            "prUrl": pr_url,
        }

        # Add issue_uuid to the payload for leader tasks
        if node_type == "leader":
            # If issue_uuid not provided directly, try to get it from the database
            if not issue_uuid and task_id and round_number is not None:
                try:
                    db = get_db()
                    submission = (
                        db.query(Submission)
                        .filter(
                            Submission.task_id == task_id,
                            Submission.round_number == round_number,
                        )
                        .first()
                    )
                    if submission and submission.issue_uuid:
                        issue_uuid = submission.issue_uuid
                        logger.info(f"Retrieved issue_uuid={issue_uuid} from database")
                except Exception as e:
                    logger.warning(f"Failed to get issue_uuid from database: {str(e)}")

            if issue_uuid:
                payload["issueUuid"] = issue_uuid
            else:
                logger.warning("No issue_uuid available for leader PR recording")

        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + endpoint,
            json=payload,
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


def _store_pr_locally(
    round_number: int,
    pr_url: str,
    task_id: str,
    issue_uuid: str = None,
    node_type: str = "worker",
) -> dict:
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

            # Update issue_uuid and node_type if provided
            if issue_uuid:
                submission.issue_uuid = issue_uuid
            submission.node_type = node_type

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
    """Record PR URL both remotely and locally.

    Args:
        staking_key: Node's staking key
        staking_signature: Node's signature
        pub_key: Node's public key
        pr_url: URL of the PR to record
        round_number: Round number
        task_id: Task ID
        node_type: Type of node ("worker" or "leader") to determine which endpoint to use
    """
    # First check if we already have a record locally
    existing = _check_existing_pr(round_number, task_id)
    existing_pr_url = None
    if existing["success"]:
        # Even if we have a local record, still attempt to record remotely
        # but use the existing PR URL from the local record
        existing_pr_url = existing["data"]["pr_url"]
        logger.info(
            f"Using existing PR URL: {existing_pr_url} for remote recording attempt"
        )
        pr_url = existing_pr_url

    # For leader tasks, we need to get the issue UUID
    issue_uuid = None
    if node_type == "leader":
        # Get task details to retrieve issue_uuid
        task_details = get_task_details(
            staking_signature, staking_key, pub_key, "leader"
        )
        if task_details.get("success", False) and "data" in task_details:
            issue_uuid = task_details["data"].get("issue_uuid")
            if not issue_uuid:
                logger.warning("No issue_uuid found in task details for leader task")

    # Step 1: Always attempt to record with middle server, even for existing PRs
    remote_result = _store_pr_remotely(
        staking_key,
        staking_signature,
        pub_key,
        pr_url,
        node_type,
        issue_uuid,
        task_id,
        round_number,
    )
    if not remote_result["success"]:
        # If the error is because the PR is already recorded, treat it as a success
        if "already" in str(remote_result.get("error", "")).lower():
            logger.info("PR already recorded remotely, continuing")
        else:
            # For other errors, return the error
            return remote_result

    # Step 2: Record locally if not already recorded
    if existing["success"] and existing.get("skip_local_recording"):
        logger.info("Skipping local recording as PR already exists locally")

        # But we should update the issue_uuid and node_type if we have new information
        if existing_pr_url and (issue_uuid or node_type):
            try:
                db = get_db()
                submission = (
                    db.query(Submission)
                    .filter(
                        Submission.round_number == round_number,
                        Submission.task_id == task_id,
                    )
                    .first()
                )
                if submission:
                    if issue_uuid and not submission.issue_uuid:
                        submission.issue_uuid = issue_uuid
                    if node_type:
                        submission.node_type = node_type
                    db.commit()
                    logger.info(
                        f"Updated submission with issue_uuid={issue_uuid}, node_type={node_type}"
                    )
            except Exception as e:
                logger.warning(f"Failed to update existing submission: {str(e)}")
    else:
        local_result = _store_pr_locally(
            round_number, pr_url, task_id, issue_uuid, node_type
        )
        if not local_result["success"]:
            return local_result

    return {
        "success": True,
        "data": {"message": "PR recorded successfully", "pr_url": pr_url},
    }


def consolidate_prs(
    task_id,
    round_number,
    staking_key,
    pub_key,
    staking_signature,
    public_signature,
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

        # If we have an existing PR, we'll use it
        pr_url = None
        if existing_submission and existing_submission.pr_url:
            pr_url = existing_submission.pr_url
            logger.info(
                f"Found existing PR URL for task {task_id}, round {round_number}: {pr_url}"
            )
            # We'll use the existing PR URL
        else:
            # Get task details which includes issue_uuid
            issue_result = get_task_details(
                staking_signature, staking_key, pub_key, "leader"
            )

            if not issue_result.get("success", False):
                return {
                    "success": False,
                    "status": issue_result.get("status", 500),
                    "error": issue_result.get("error", "Unknown error fetching todo"),
                }

            issue = issue_result["data"]
            repo_owner = issue["repo_owner"]
            repo_name = issue["repo_name"]
            source_branch = issue["issue_uuid"]
            issue_uuid = issue["issue_uuid"]  # Store issue_uuid for later use
            pr_list = issue["pr_list"]

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
                issue_uuid=issue_uuid,  # Store issue_uuid
                node_type="leader",  # Set node_type to leader
            )
            db.add(submission)
            db.commit()

            # Get source fork
            github = Github(os.environ["GITHUB_TOKEN"])
            source_fork = github.get_repo(f"{repo_owner}/{repo_name}")

            # Verify this is a fork
            if not source_fork.fork:
                submission.status = "failed"
                db.commit()
                return {
                    "success": False,
                    "status": 400,
                    "error": "Source repository is not a fork",
                }

            # Create workflow instance with validated PRs
            logger.info("\nCreating workflow with:")
            logger.info(f"  task_id: {task_id}")

            # Initialize Claude client
            client = setup_client("anthropic")

            workflow = MergeConflictWorkflow(
                client=client,
                prompts=CONFLICT_PROMPTS,
                source_fork_url=source_fork.html_url,
                source_branch=source_branch,
                staking_key=staking_key,
                pub_key=pub_key,
                staking_signature=staking_signature,
                public_signature=public_signature,
                task_id=task_id,  # Add task_id for signature validation
                pr_list=pr_list,
                expected_branch=source_branch,
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

            # Store PR URL in local DB
            submission.pr_url = pr_url
            submission.status = (
                "pending_record"  # Will be updated to completed by record_pr
            )
            db.commit()
            logger.info(
                f"Stored PR URL {pr_url} locally for task {task_id}, round {round_number}"
            )

        # Use record_pr to handle both local and remote recording
        record_result = record_pr(
            staking_key=staking_key,
            staking_signature=staking_signature,
            pub_key=pub_key,
            pr_url=pr_url,
            round_number=round_number,
            task_id=task_id,
            node_type="leader",
        )

        if not record_result["success"]:
            logger.warning(f"PR recording had issues: {record_result}")
            # Continue anyway since we have the PR

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


def create_aggregator_repo(task_id):
    """Create an aggregator repo for a given round and task.

    Args:
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

        # Get issue UUID and repo info from assign_issue response
        logger.info(f"Calling assign_issue with username: {username}")
        issue_data = assign_issue(task_id)
        logger.info(f"assign_issue response: {issue_data}")

        if not issue_data.get("success"):
            logger.error(f"assign_issue failed: {issue_data.get('error')}")
            return {
                "success": False,
                "message": f"Failed to assign issue: {issue_data.get('error')}",
                "data": None,
            }

        logger.info(f"assign_issue data: {issue_data.get('data')}")
        issue_uuid = issue_data["data"].get("issueId")
        # Get repo info from the issue data instead of parameters
        repo_owner = issue_data["data"].get("repoOwner")
        repo_name = issue_data["data"].get("repoName")

        logger.info(f"Using repo from issue: {repo_owner}/{repo_name}")
        logger.info(f"Extracted issue_uuid: {issue_uuid}")

        if not issue_uuid or not repo_owner or not repo_name:
            logger.error("Missing required data in assign_issue response")
            return {
                "success": False,
                "message": "Missing required data (issueId, repoOwner, or repoName) from assign_issue",
                "data": None,
            }

        # Get source repo from the repo information obtained from the middle server
        try:
            source_repo = github.get_repo(f"{repo_owner}/{repo_name}")
            logger.info(f"Found source repo: {source_repo.html_url}")
        except Exception as e:
            logger.error(
                f"Error finding source repo {repo_owner}/{repo_name}: {str(e)}"
            )
            return {
                "success": False,
                "message": f"Failed to find source repo {repo_owner}/{repo_name}: {str(e)}",
                "data": None,
            }

        # Check if fork already exists
        try:
            fork = github.get_repo(f"{username}/{repo_name}")
            logger.info(f"Using existing fork: {fork.html_url}")
        except Exception:
            # Create new fork if it doesn't exist
            fork = github.get_user().create_fork(source_repo)
            logger.info(f"Created new fork: {fork.html_url}")

        branch_name = issue_uuid
        logger.info(f"Using branch_name: {branch_name}")

        try:
            # Check if branch already exists
            try:
                fork.get_branch(branch_name)
                logger.info(f"Using existing branch: {branch_name}")
            except Exception:
                # Create a branch with the issue UUID name
                # Branch doesn't exist, create it
                default_branch = fork.default_branch
                default_branch_sha = fork.get_branch(default_branch).commit.sha
                fork.create_git_ref(f"refs/heads/{branch_name}", default_branch_sha)
                logger.info(f"Created new branch: {branch_name}")

            # The create-aggregator-repo endpoint should only create the fork and branch
            # It should not call the middle server directly

            return {
                "success": True,
                "message": "Successfully created aggregator repository",
                "data": {"fork_url": fork.html_url, "branch_name": branch_name},
            }

        except Exception as e:
            logger.error(
                f"Error in branch creation or aggregator info recording: {str(e)}"
            )
            return {
                "success": False,
                "message": f"Failed to create branch or record aggregator info: {str(e)}",
                "data": None,
            }

    except Exception as e:
        logger.error(f"Error in create_aggregator_repo: {str(e)}")
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
        logger.info(
            f"Making assign_issue request to {os.environ['MIDDLE_SERVER_URL']}/api/assign-issue"
        )
        logger.info(
            f"Request payload: {{'taskId': {task_id}, 'githubUsername': {os.environ['GITHUB_USERNAME']}}}"
        )

        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + "/api/assign-issue",
            json={"taskId": task_id, "githubUsername": os.environ["GITHUB_USERNAME"]},
            headers={"Content-Type": "application/json"},
        )
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Response body: {response.text}")

        response.raise_for_status()
        result = response.json()

        logger.info(f"assign_issue result: {result}")

        if not result.get("success", False):
            logger.error(f"assign_issue failed: {result.get('message')}")
            return {
                "success": False,
                "status": 400,
                "error": result.get("message", "Unknown error from middle server"),
            }

        logger.info(f"assign_issue succeeded: {result}")
        # Return the entire result as data since it contains the issueId
        return {"success": True, "data": result}

    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception in assign_issue: {str(e)}")
        if not hasattr(e, "response") or e.response is None:
            return {
                "success": False,
                "status": 500,
                "error": "No response from middle server",
            }

        try:
            error_data = e.response.json()
            error_message = error_data.get("message", "Unknown error")
            logger.error(f"Error response: {error_message}")
        except ValueError:
            error_message = e.response.text
            logger.error(f"Raw error response: {error_message}")

        return {
            "success": False,
            "status": e.response.status_code,
            "error": error_message,
        }


def add_aggregator_info(task_id, staking_key, pub_key, signature):
    """Add aggregator info to the middle server.

    Args:
        task_id (str): The task ID
        staking_key (str): The staking key
        pub_key (str): The public key
        signature (str): The signature

    Returns:
        dict: The result of the operation
    """
    logger.info(f"Adding aggregator info for task {task_id}")
    try:
        payload = {
            "stakingKey": staking_key,
            "pubKey": pub_key,
            "signature": signature,
        }

        # Send the request to the middle server
        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + "/api/add-aggregator-info",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        result = response.json()

        if not result.get("success", False):
            logger.error(f"Failed to add aggregator info: {result.get('message')}")
            return {
                "success": False,
                "message": f"Failed to add aggregator info: {result.get('message')}",
            }

        logger.info("Successfully added aggregator info")
        return {
            "success": True,
            "message": "Successfully added aggregator info",
            "data": result.get("data", {}),
        }

    except Exception as e:
        logger.error(f"Error in add_aggregator_info: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to add aggregator info: {str(e)}",
        }
