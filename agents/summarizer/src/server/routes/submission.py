from flask import Blueprint, jsonify
from src.database import get_db, Submission
import logging
import os
logger = logging.getLogger(__name__)

bp = Blueprint("submission", __name__)


@bp.get("/submission/<roundNumber>")
def fetch_submission(roundNumber):
    logger.info(f"Fetching submission for round: {roundNumber}")

    db = get_db()
    submission = (
        db.query(Submission)
        .filter(
            Submission.round_number == int(roundNumber),
            Submission.status == "completed",
        )
        .first()
    )

    if submission:

        github_username = os.getenv("GITHUB_USERNAME")
        return jsonify(
            {
                "taskId": submission.task_id,
                "roundNumber": submission.round_number,
                "status": submission.status,
                "repoUrl": submission.repo_url,
                "prUrl": submission.pr_url,
                "username": github_username,
            }
        )
    else:
        return jsonify({"error": "Submission not found"}), 404
