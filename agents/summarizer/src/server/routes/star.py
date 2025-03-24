from flask import Blueprint, jsonify, request
from src.server.services import star_service

bp = Blueprint("star", __name__)


@bp.post("/star/<round_number>")
def start_task(round_number):
    logger = star_service.logger
    logger.info(f"Task started for round: {round_number}")

    data = request.get_json()
    logger.info(f"Task data: {data}")
    required_fields = [
        "taskId",
        "round_number",
        "github_urls",
    ]
    if any(data.get(field) is None for field in required_fields):
        return jsonify({"error": "Missing data"}), 401

    result = star_service.handle_star_task(
        task_id=data["taskId"],
        round_number=int(round_number),
        github_urls=data["github_urls"],
    )

    return jsonify({"message": result})
