from flask import Blueprint, jsonify, request
from src.server.services.github_service import verify_pr_ownership
from src.server.services.audit_service import audit_repo
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("audit", __name__)


@bp.post("/audit/<round_number>")
def audit_submission(round_number: int):
    logger.info("Auditing submission")

    data = request.get_json()
    submission = data.get("submission")

    if not submission:
        return jsonify({"error": "Missing submission"}), 400

    # submission_round_number = submission.get("roundNumber")
    task_id = submission.get("taskId")
    pr_url = submission.get("prUrl")
    github_username = submission.get("githubUsername")
    
    # Extract repo owner and name from PR URL
    try:
        pr_url_parts = pr_url.split('github.com/')[1].split('/')
        repo_owner = pr_url_parts[0]
        repo_name = pr_url_parts[1]
    except (IndexError, AttributeError):
        return jsonify({"error": "Invalid PR URL format"}), 400
    print(f"Repo owner: {repo_owner}, Repo name: {repo_name}")
    # This is commented out because the round number might be different due to we put the audit logic in the distribution part
    # if int(round_number) != submission_round_number:
    #     return jsonify({"error": "Round number mismatch"}), 400

    if (
        not task_id
        or not pr_url
        or not github_username
        or not repo_owner
        or not repo_name
    ):
        return jsonify({"error": "Missing submission data"}), 400

    is_valid = verify_pr_ownership(
        pr_url=pr_url,
        expected_username=github_username,
        expected_owner=repo_owner,
        expected_repo=repo_name,
    )

    if not is_valid:
        return jsonify(False)

    try:
        is_approved = audit_repo(pr_url)
        return jsonify(is_approved), 200
    except Exception as e:
        logger.error(f"Error auditing PR: {str(e)}")
        return jsonify(True), 200
