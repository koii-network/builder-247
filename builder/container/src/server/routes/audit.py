from flask import Blueprint, jsonify, request
from src.server.services import database
from src.server.services.github_service import verify_pr_ownership
import json
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("audit", __name__, url_prefix="/audit")


@bp.route("", methods=["POST"])
def audit_submission():
    logger.info("Auditing submission")

    data = request.get_json()
    submission = data.get("submission")
    signature = data.get("signature")
    staking_key = data.get("stakingKey")

    if not submission:
        return jsonify({"error": "Missing submission"}), 400

    submission_json = json.loads(submission)

    round_number = submission_json.get("roundNumber")

    if not round_number:
        return jsonify({"error": "Missing round number"}), 400

    if not signature or not staking_key:
        return jsonify({"error": "Missing signature or staking key"}), 401

    db = database.get_db()
    cursor = db.cursor()
    query = cursor.execute(
        """
        SELECT pr_url, username, repo_owner, repo_name
        FROM submissions
        WHERE roundNumber = ? AND status = 'completed'
        """,
        (int(round_number),),
    )
    result = query.fetchone()
    database.close_db()

    if not result:
        return jsonify({"error": "Submission not found"}), 404

    is_valid = verify_pr_ownership(
        result["pr_url"],
        result["username"],
        result["repo_owner"],
        result["repo_name"],
        signature,
        staking_key,
    )
    return jsonify(is_valid)
