"""Task service module."""

import requests
import os
from flask import jsonify
from src.database import get_db, Submission
from src.clients import setup_client
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.mergeconflict.workflow import MergeConflictWorkflow
from src.workflows.mergeconflict.prompts import PROMPTS as CONFLICT_PROMPTS
from src.workflows.task.prompts import PROMPTS as TASK_PROMPTS
from src.utils.logging import logger, log_error
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

    source_repo = fetch_source_repo(task_id, round_number)

    # Initialize Claude client
    client = setup_client("anthropic")

    # Use the workflow to process all PRs with the limit
    workflow = MergeConflictWorkflow(
        client=client,
        prompts=CONFLICT_PROMPTS,
        repo_url=source_repo,
        target_branch=args.branch,
        pr_limit=args.limit,
    )

    result = workflow.run()

    # Print summary
    print("\n=== MERGE SUMMARY ===")
    if result and result.get("success"):
        merged_prs = result["data"].get("merged_prs", [])
        failed_prs = result["data"].get("failed_prs", [])
        closed_prs = [pr for pr in failed_prs if result["data"].get("should_close")]
        error_prs = [pr for pr in failed_prs if pr not in closed_prs]
        total_prs = len(merged_prs) + len(failed_prs)

        print(f"Total PRs processed: {total_prs}")
        print(f"Successfully merged: {len(merged_prs)}")

        if closed_prs:
            print(f"Closed without merging: {len(closed_prs)}")
            print("Closed PRs:", ", ".join(f"#{pr}" for pr in closed_prs))

        if error_prs:
            print(f"Failed to process: {len(error_prs)}")
            print("Failed PRs:", ", ".join(f"#{pr}" for pr in error_prs))
    else:
        error_message = (
            result.get("message", "Unknown error")
            if result
            else "Workflow returned no result"
        )
        print(f"Error running workflow: {error_message}")

    return 0


def fetch_source_repo(task_id, round_number):
    response = requests.post(
        os.environ["MIDDLE_SERVER_URL"] + "/api/fetch-source-repo",
        json={
            "taskId": task_id,
            "roundNumber": round_number,
        },
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response.json()
