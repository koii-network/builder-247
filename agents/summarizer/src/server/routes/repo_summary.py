from flask import Blueprint, jsonify, request
from src.server.services import repo_summary_service

bp = Blueprint("repo_summary", __name__)


@bp.post("/repo_summary/<round_number>")
def start_task(round_number):
    logger = repo_summary_service.logger
    logger.info(f"Task started for round: {round_number}")

    data = request.get_json()
    logger.info(f"Task data: {data}")
    required_fields = [
        "taskId",
        "round_number",
        "repo_url"
    ]
    if any(data.get(field) is None for field in required_fields):
        return jsonify({"error": "Missing data"}), 401

    result = repo_summary_service.handle_task_creation(
        task_id=data["taskId"],
        round_number=int(round_number),
        repo_url=data["repo_url"],
    )

    return jsonify({"message": result})
