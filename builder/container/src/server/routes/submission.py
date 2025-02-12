from flask import Blueprint, jsonify
from src.server.services import database

bp = Blueprint("submission", __name__, url_prefix="/submission")


@bp.route("/<roundNumber>")
def fetch_submission(roundNumber):
    logger = database.logger
    logger.info(f"Fetching submission for round: {roundNumber}")

    db = database.get_db()
    cursor = db.cursor()
    query = cursor.execute(
        """
        SELECT roundNumber, status, pr_url, username
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
                "status": result["status"],
                "pr_url": result["pr_url"],
                "username": result["username"],
            }
        )
    else:
        return "Submission not found", 404
