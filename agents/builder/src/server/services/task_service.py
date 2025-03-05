"""Task service module."""

import requests
import os
from flask import jsonify
from src.database import get_db, Submission
from src.clients import setup_client
from src.workflows.task.workflow import TaskWorkflow
from src.workflows.task.prompts import PROMPTS as TASK_PROMPTS
import logging

logger = logging.getLogger(__name__)


def handle_task_creation(task_id, round_number, signature, staking_key, pub_key):
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
            logger.error(
                f"Failed to fetch todo: {result.get('message', 'Unknown error')}"
            )
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching todo: {str(e)}")
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
        logger.error(f"PR creation failed: {str(e)}")
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


def submit_pr(signature, staking_key, pub_key, pr_url, round_number):
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
            logger.error(f"No submission found for round {round_number}")
            return "Error: Submission not found"

    except requests.exceptions.RequestException as e:
        logger.error(f"Error submitting PR: {str(e)}")
        return "Error submitting PR"
