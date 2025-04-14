from src.utils.logging import log_key_value
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

    try:
        # Log incoming data
        print("Received data:", data)
        print("Round number:", round_number)
        
        result = star_service.handle_star_task(
            task_id=data["taskId"],
            round_number=int(round_number),
            github_urls=data["github_urls"],
        )
        return result
    except Exception as e:
        print(f"Error in star endpoint: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
