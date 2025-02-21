from flask import Blueprint, jsonify
from src.server.services import database
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("submission", __name__)


@bp.route("/submission/<roundNumber>")
def fetch_submission(roundNumber):
    logger.info(f"Fetching submission for round: {roundNumber}")

    db = database.get_db()
    cursor = db.cursor()
    query = cursor.execute(
        """
        SELECT roundNumber, status, pr_url, username, repo_owner, repo_name
        FROM submissions
        WHERE roundNumber = ? and status = 'completed'
        """,
        (int(roundNumber),),
    )
    result = query.fetchone()
    database.close_db()

    if result:
        return jsonify(
            {
                "roundNumber": result["roundNumber"],
                "prUrl": result["pr_url"],
                "githubUsername": result["username"],
                "repoOwner": result["repo_owner"],
                "repoName": result["repo_name"],
            }
        )
    else:
        return "Submission not found", 404
