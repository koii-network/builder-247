from flask import Blueprint, jsonify, request
from src.server.services.task_service import submit_pr

bp = Blueprint("submit_pr", __name__)


@bp.post("/submit-pr/<roundNumber>")
def submit_pr_route(roundNumber):
    data = request.get_json()
    signature = data.get("signature")
    staking_key = data.get("stakingKey")
    pub_key = data.get("pubKey")
    pr_url = data.get("prUrl")

    if not pr_url:
        return jsonify({"error": "Missing PR URL"}), 400

    message = submit_pr(signature, staking_key, pub_key, pr_url, roundNumber)

    return jsonify({"message": message})
