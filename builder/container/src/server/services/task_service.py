import requests
import os
from threading import Thread
from flask import jsonify
from src.server.services.database import get_db, close_db
from src.task.flow import todo_to_pr
import logging

logger = logging.getLogger(__name__)


def handle_task_creation(round_number, fetch_signature, add_signature, staking_key):
    todo = get_todo(fetch_signature, staking_key)
    if not todo:
        return jsonify({"error": "No todo found"}), 404

    Thread(
        target=run_todo_task, args=(int(round_number), todo, add_signature, staking_key)
    ).start()

    return jsonify({"roundNumber": round_number, "status": "Task started"})


def get_todo(signature, staking_key):
    try:
        logger.info("Fetching todo")
        response = requests.post(
            os.environ.get("MIDDLE_SERVER_URL") + "/api/fetch-to-do",
            json={
                "signature": signature,
                "pubKey": staking_key,
                "github_username": os.environ.get("GITHUB_USERNAME"),
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


def run_todo_task(round_number, todo, signature, staking_key):
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO submissions
            (roundNumber, status, repo_owner, repo_name)
            VALUES (?, ?, ?, ?)
            """,
            (round_number, "running", todo["repo_owner"], todo["repo_name"]),
        )
        db.commit()

        pr_url = todo_to_pr(
            todo=todo["title"],
            acceptance_criteria=todo["acceptance_criteria"],
            repo_owner=todo["repo_owner"],
            repo_name=todo["repo_name"],
        )

        try:
            response = requests.post(
                os.environ.get("MIDDLE_SERVER_URL") + "/api/add-pr-to-to-do",
                json={
                    "pr_url": pr_url,
                    "signature": signature,
                    "pubKey": staking_key,
                },
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error submitting PR: {str(e)}")

        username = os.environ.get("GITHUB_USERNAME")

        cursor.execute(
            """
            UPDATE submissions
            SET status = ?, pr_url = ?, username = ?
            WHERE roundNumber = ?
            """,
            ("completed", pr_url, username, round_number),
        )
        db.commit()
    except Exception as e:
        logger.error(f"Background task failed: {str(e)}")
        if "cursor" in locals():
            cursor.execute(
                "UPDATE submissions SET status = ? WHERE roundNumber = ?",
                ("failed", round_number),
            )
            db.commit()
    finally:
        close_db()
