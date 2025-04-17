from flask import Blueprint, jsonify
from prometheus_swarm.database import get_db, Submission
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
        )
        .first()
    )
    logger.info(f"Submission: {submission}")
    logger.info(f"Submission: {submission}")
    if submission:

        github_username = os.getenv("GITHUB_USERNAME")
        return jsonify(
            {
                "taskId": submission.task_id,
                "roundNumber": submission.round_number,
                "status": submission.status,
                "prUrl": submission.pr_url,
                "githubUsername": github_username,
            }
        )
    else:
        return jsonify({"error": "Submission not found"}), 409
