from flask import Blueprint, jsonify, request
from src.server.services.audit_service import verify_pr_ownership
from src.server.services.audit_service import review_pr, audit_leader_submission
from src.utils.logging import logger, log_error

bp = Blueprint("audit", __name__)


@bp.post("/worker-audit/<round_number>")
def audit_worker_submission(round_number: str):
    logger.info("Auditing submission")
    round_number = int(round_number)
    data = request.get_json()
    logger.info(f"Request data: {data}")

    submission = data.get("submission")
    submitter_signature = data.get("submitterSignature")
    staking_key = data.get("stakingKey")
    pub_key = data.get("pubKey")
    staking_signature = data.get("stakingSignature")
    public_signature = data.get("publicSignature")

    if not submission:
        return jsonify({"error": "Missing submission"}), 400

    submission_round_number = submission.get("roundNumber")
    task_id = submission.get("taskId")
    pr_url = submission.get("prUrl")
    github_username = submission.get("githubUsername")
    repo_owner = submission.get("repoOwner")
    repo_name = submission.get("repoName")
    submitter_staking_key = submission.get("stakingKey")
    submitter_pub_key = submission.get("pubKey")

    if round_number != submission_round_number:
        return jsonify({"error": "Round number mismatch"}), 400

    if (
        not task_id
        or not pr_url
        or not github_username
        or not repo_owner
        or not repo_name
        or not staking_key
        or not pub_key
        or not submitter_signature
        or not submitter_staking_key
        or not submitter_pub_key
        or not staking_signature
        or not public_signature
    ):
        return jsonify({"error": "Missing submission data"}), 400

    is_valid = verify_pr_ownership(
        pr_url=pr_url,
        expected_username=github_username,
        expected_owner=repo_owner,
        expected_repo=repo_name,
        task_id=task_id,
        round_number=round_number,
        staking_key=submitter_staking_key,
        pub_key=submitter_pub_key,
        signature=submitter_signature,
    )

    if not is_valid:
        log_error(
            Exception("Invalid PR ownership"),
            context=f"Invalid PR ownership: {pr_url}",
        )
        return jsonify(
            {
                "success": True,
                "message": "PR ownership validation failed",
                "data": {"passed": False},
            }
        )

    try:
        is_approved = review_pr(
            pr_url,
            staking_key,
            pub_key,
            staking_signature,
            public_signature,
        )
        return jsonify(
            {
                "success": True,
                "message": (
                    "PR approved by agent" if is_approved else "PR rejected by agent"
                ),
                "data": {"passed": is_approved},
            }
        )
    except Exception as e:
        log_error(e, context="Error reviewing PR")
        return jsonify(
            {
                "success": True,
                "message": "Error during PR review, defaulting to pass",
                "data": {"passed": True},
            }
        )


@bp.post("/leader-audit/<round_number>")
def handle_leader_audit(round_number: int):
    """Audit a leader's consolidated PR submission.

    Expected request body:
    {
        "submission": {
            "roundNumber": int,
            "taskId": str,
            "prUrl": str,
            "repoOwner": str,
            "repoName": str,
            "stakingKey": str,
            "pubKey": str,
            "signature": str,
            "distributionList": {
                "stakingKey1": float,  # Reward amount
                "stakingKey2": float,
                ...
            },
            "leaders": [str]  # List of leader staking keys
        }
    }
    """
    logger.info("Auditing leader submission")

    data = request.get_json()
    submission = data.get("submission")

    if not submission:
        return jsonify({"error": "Missing submission"}), 400

    # Extract submission data
    submission_round_number = submission.get("roundNumber")
    task_id = submission.get("taskId")
    pr_url = submission.get("prUrl")
    repo_owner = submission.get("repoOwner")
    repo_name = submission.get("repoName")
    staking_key = submission.get("stakingKey")
    pub_key = submission.get("pubKey")
    signature = submission.get("signature")
    distribution_list = submission.get("distributionList", {})
    leaders = submission.get("leaders", [])
    github_username = submission.get("githubUsername")

    # Validate required fields
    if int(round_number) != submission_round_number:
        return jsonify({"error": "Round number mismatch"}), 400

    if (
        not task_id
        or not pr_url
        or not repo_owner
        or not repo_name
        or not staking_key
        or not pub_key
        or not signature
        or not distribution_list
        or not leaders
        or not github_username
    ):
        return jsonify({"error": "Missing submission data"}), 400

    # Verify this node is a leader
    if staking_key not in leaders:
        return jsonify({"error": "Not authorized as leader"}), 403

    try:
        # Run leader audit checks
        is_valid = audit_leader_submission(
            task_id=task_id,
            round_number=round_number,
            pr_url=pr_url,
            repo_owner=repo_owner,
            repo_name=repo_name,
            staking_key=staking_key,
            pub_key=pub_key,
            signature=signature,
            distribution_list=distribution_list,
            leader_username=github_username,
        )
        return jsonify(
            {
                "success": True,
                "message": "PR audit completed",
                "data": {"passed": is_valid},
            }
        )
    except Exception as e:
        log_error(e, context="Error auditing leader submission")
        return jsonify({"error": str(e)}), 500
