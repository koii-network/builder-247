from flask import Blueprint, jsonify, request
from src.server.services.task_service import submit_pr

bp = Blueprint("submit_pr", __name__)


@bp.route("/submit-pr/<roundNumber>", methods=["POST"])
def get_github_username(roundNumber):
    data = request.get_json()
    signature = data.get("signature")
    staking_key = data.get("stakingKey")
    pr_url = data.get("prUrl")

    message = submit_pr(signature, staking_key, pr_url, roundNumber)

    return jsonify({"message": message})
