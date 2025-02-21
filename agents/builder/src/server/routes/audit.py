from flask import Blueprint, jsonify, request
from src.server.services.github_service import verify_pr_ownership
from src.server.services.task_service import approve_pr
import json
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("audit", __name__)


@bp.route("/audit", methods=["POST"])
def audit_submission():
    logger.info("Auditing submission")

    data = request.get_json()
    submission = data.get("submission")
    signature = data.get("signature")
    staking_key = data.get("stakingKey")

    if not submission:
        return jsonify({"error": "Missing submission"}), 400

    submission_json = json.loads(submission)

    print(submission_json)

    round_number = submission_json.get("roundNumber")
    task_id = submission_json.get("taskId")
    pr_url = submission_json.get("prUrl")
    github_username = submission_json.get("githubUsername")
    repo_owner = submission_json.get("repoOwner")
    repo_name = submission_json.get("repoName")
    staking_key = submission_json.get("stakingKey")
    if (
        not round_number
        or not task_id
        or not pr_url
        or not github_username
        or not repo_owner
        or not repo_name
        or not staking_key
    ):
        return jsonify({"error": "Missing submission data"}), 400

    is_valid = verify_pr_ownership(
        pr_url=pr_url,
        expected_username=github_username,
        expected_owner=repo_owner,
        expected_repo=repo_name,
        signature=signature,
        staking_key=staking_key,
    )

    if (is_valid):
        is_approved =
    return jsonify(is_approved)
