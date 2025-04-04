from flask import Blueprint, jsonify, request
from src.database import get_db, Submission
from agent_framework.utils.logging import logger

bp = Blueprint("submission", __name__)


@bp.get("/submission/<roundNumber>")
def fetch_submission(roundNumber):
    """Fetch submission for a given round and task.

    Query parameters:
        taskId: The task ID to fetch submission for
    """
    logger.info(f"Fetching submission for round: {roundNumber}")

    task_id = request.args.get("taskId")
    if not task_id:
        return jsonify({"error": "Missing taskId parameter"}), 400

    db = get_db()
    submission = (
        db.query(Submission)
        .filter(
            Submission.round_number == int(roundNumber),
            Submission.task_id == task_id,
            Submission.status == "completed",
        )
        .first()
    )

    if submission:
        return jsonify(
            {
                "roundNumber": submission.round_number,
                "taskId": submission.task_id,  # Include task ID in response
                "prUrl": submission.pr_url,
                "githubUsername": submission.username,
                "repoOwner": submission.repo_owner,
                "repoName": submission.repo_name,
                "nodeType": submission.node_type,
            }
        )
    else:
        return jsonify("No submission")
