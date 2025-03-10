from flask import Blueprint, jsonify, request
from src.server.services.github_service import verify_pr_ownership
from src.server.services.audit_service import review_pr
from src.utils.logging import logger, log_error

bp = Blueprint("audit", __name__)


@bp.post("/worker-audit/<round_number>")
def audit_worker_submission(round_number: int):
    logger.info("Auditing submission")

    data = request.get_json()
    submission = data.get("submission")
    signature = data.get("signature")
    staking_key = data.get("stakingKey")

    if not submission:
        return jsonify({"error": "Missing submission"}), 400

    submission_round_number = submission.get("roundNumber")
    task_id = submission.get("taskId")
    pr_url = submission.get("prUrl")
    github_username = submission.get("githubUsername")
    repo_owner = submission.get("repoOwner")
    repo_name = submission.get("repoName")
    staking_key = submission.get("stakingKey")
    pub_key = submission.get("pubKey")

    if int(round_number) != submission_round_number:
        return jsonify({"error": "Round number mismatch"}), 400

    if (
        not task_id
        or not pr_url
        or not github_username
        or not repo_owner
        or not repo_name
        or not staking_key
        or not pub_key
    ):
        return jsonify({"error": "Missing submission data"}), 400

    is_valid = verify_pr_ownership(
        pr_url=pr_url,
        expected_username=github_username,
        expected_owner=repo_owner,
        expected_repo=repo_name,
        signature=signature,
        staking_key=staking_key,
        pub_key=pub_key,
    )

    if not is_valid:
        return jsonify(False)

    try:
        is_approved = review_pr(pr_url)
        return jsonify(is_approved)
    except Exception as e:
        log_error(e, context="Error reviewing PR")
        return jsonify(True)


@bp.post("/leader-audit/<round_number>")
def audit_leader_submission(round_number: int):
    logger.info("Auditing leader submission")
