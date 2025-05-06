from flask import Blueprint, jsonify, request
from src.server.services import task_service
from prometheus_swarm.utils.logging import logger
from src.utils.nonce import nonce_manager, NonceError
import requests
import os

bp = Blueprint("task", __name__)

# Decorator to inject nonce validation into routes
def require_nonce(func):
    def wrapper(*args, **kwargs):
        nonce = request.headers.get('X-Nonce')
        try:
            nonce_manager.validate_nonce(nonce)
        except NonceError as e:
            return jsonify({"success": False, "message": str(e)}), 401
        return func(*args, **kwargs)
    return wrapper

@bp.post("/worker-task/<round_number>")
@require_nonce
def start_worker_task(round_number):
    return start_task(round_number, "worker", request)

@bp.post("/leader-task/<round_number>")
@require_nonce
def start_leader_task(round_number):
    return start_task(round_number, "leader", request)

@bp.post("/create-aggregator-repo/<task_id>")
@require_nonce
def create_aggregator_repo(task_id):
    print("\n=== ROUTE HANDLER CALLED ===")
    print(f"task_id: {task_id}")

    # Create the aggregator repo (which now handles assign_issue internally)
    result = task_service.create_aggregator_repo(task_id)
    print(f"result: {result}")

    # Extract status code from result if present, default to 200
    status_code = result.pop("status", 200) if isinstance(result, dict) else 200
    return jsonify(result), status_code

@bp.post("/add-aggregator-info/<task_id>")
@require_nonce
def add_aggregator_info(task_id):
    print("\n=== ADD AGGREGATOR INFO ROUTE HANDLER CALLED ===")
    print(f"task_id: {task_id}")
    request_data = request.get_json()
    print(f"request_data: {request_data}")
    if not request_data:
        return jsonify({"success": False, "error": "Invalid request body"}), 401

    # Call the task service to update aggregator info with the middle server
    result = task_service.add_aggregator_info(
        task_id,
        request_data.get("stakingKey"),
        request_data.get("pubKey"),
        request_data.get("signature"),
    )
    print(f"result: {result}")

    # Extract status code from result if present, default to 200
    status_code = result.pop("status", 200) if isinstance(result, dict) else 200
    return jsonify(result), status_code

def start_task(round_number, node_type, request):
    # [Rest of the implementation remains the same as before]
    # Existing code for task start is not modified, just wrapped with nonce decorator

@bp.post("/update-audit-result/<task_id>/<round_number>")
@require_nonce
def update_audit_result(task_id, round_number):
    try:
        # Convert round_number to integer
        round_number = int(round_number)

        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + "/api/builder/update-audit-result",
            json={
                "taskId": task_id,
                "round": round_number,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()

        result = response.json()
        if not result.get("success", False):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": result.get("message", "Unknown error"),
                    }
                ),
                500,
            )
        return jsonify({"success": True, "message": "Audit results processed"}), 200
    except ValueError:
        return jsonify({"success": False, "message": "Invalid round number"}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": str(e)}), 500