"""Task service module."""

import requests
import os
from flask import jsonify
from src.database import get_db, Submission
from src.workflows.flow_new import todo_to_pr
from src.workflows.review_flow_new import review_pr
from src.workflows.prompts import REVIEW_SYSTEM_PROMPT
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

        return todo_to_pr(
            todo=todo["title"],
            acceptance_criteria=todo["acceptance_criteria"],
            repo_owner=todo["repo_owner"],
            repo_name=todo["repo_name"],
            system_prompt=todo["system_prompt"],
        )

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


def approve_pr(pr_url):
    """Review and approve PR."""
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
        "no error handling, security vulnerabilities, no tests",
        "tests are poorly designed or rely too heavily on mocking",
    )

    result = review_pr(
        pr_url=pr_url,
        requirements=requirements,
        minor_issues=minor_issues,
        major_issues=major_issues,
        system_prompt=REVIEW_SYSTEM_PROMPT,
    )
    if result.get("success"):
        return result.get("validated", True)
    else:
        raise Exception("PR review failed")
