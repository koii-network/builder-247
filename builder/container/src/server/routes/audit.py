from flask import Blueprint, jsonify, request
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

    if not submission:
        return jsonify({"error": "Missing submission"}), 400

    submission_json = json.loads(submission)

    print(submission_json)

    round_number = submission_json.get("roundNumber")
    status = submission_json.get("status")
    pr_url = submission_json.get("pr_url")
    username = submission_json.get("username")
    repo_owner = submission_json.get("repo_owner")
    repo_name = submission_json.get("repo_name")
    staking_key = submission_json.get("stakingKey")
    signature = submission_json.get("signature")
    if (
        not round_number
        or not status
        or not pr_url
        or not username
        or not repo_owner
        or not repo_name
        or not staking_key
    ):
        return jsonify({"error": "Missing submission data"}), 400

    is_valid = verify_pr_ownership(
        pr_url=pr_url,
        expected_username=username,
        expected_owner=repo_owner,
        expected_repo=repo_name,
        staking_key=staking_key,
        signature=signature,
    )
    return jsonify(is_valid)
