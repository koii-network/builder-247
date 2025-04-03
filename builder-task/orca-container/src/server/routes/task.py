from flask import Blueprint, jsonify, request
from src.server.services import task_service
from agent_framework.utils.logging import logger

bp = Blueprint("task", __name__)


@bp.post("/worker-task/<round_number>")
def start_worker_task(round_number):
    return start_task(round_number, "worker", request)


@bp.post("/leader-task/<round_number>")
def start_leader_task(round_number):
    return start_task(round_number, "leader", request)


@bp.post("/create-aggregator-repo/<task_id>")
def create_aggregator_repo(task_id):
    print("\n=== ROUTE HANDLER CALLED ===")
    print(f"task_id: {task_id}")
    request_data = request.get_json()
    print(f"request_data: {request_data}")
    if not request_data:
        return jsonify({"error": "Invalid request body"}), 401

    # Create the aggregator repo (which now handles assign_issue internally)
    result = task_service.create_aggregator_repo(task_id)
    print(f"result: {result}")
    return result


@bp.post("/add-aggregator-info/<task_id>")
def add_aggregator_info(task_id):
    print("\n=== ADD AGGREGATOR INFO ROUTE HANDLER CALLED ===")
    print(f"task_id: {task_id}")
    request_data = request.get_json()
    print(f"request_data: {request_data}")
    if not request_data:
        return jsonify({"error": "Invalid request body"}), 401

    # Call the task service to update aggregator info with the middle server
    result = task_service.add_aggregator_info(
        task_id,
        request_data.get("stakingKey"),
        request_data.get("pubKey"),
        request_data.get("signature"),
    )
    print(f"result: {result}")
    return result


def start_task(round_number, node_type, request):
    if node_type not in ["worker", "leader"]:
        return jsonify({"success": False, "error": "Invalid node type"}), 400

    task_functions = {
        "worker": task_service.complete_todo,
        "leader": task_service.consolidate_prs,
    }
    logger.info(f"{node_type.capitalize()} task started for round: {round_number}")

    request_data = request.get_json()
    logger.info(f"Task data: {request_data}")
    required_fields = [
        "taskId",
        "roundNumber",
        "stakingKey",
        "stakingSignature",
        "pubKey",
        "publicSignature",
    ]
    if any(request_data.get(field) is None for field in required_fields):
        return jsonify({"success": False, "error": "Missing data"}), 401

    response = task_functions[node_type](
        task_id=request_data["taskId"],
        round_number=int(round_number),
        staking_signature=request_data["stakingSignature"],
        staking_key=request_data["stakingKey"],
        public_signature=request_data["publicSignature"],
        pub_key=request_data["pubKey"],
    )
    response_data = response.get("data", {})
    if not response.get("success", False):
        status = response.get("status", 500)
        error = response.get("error", "Unknown error")
        return jsonify({"success": False, "error": error}), status

    logger.info(response_data["message"])

    # Record PR for both worker and leader tasks, but only workers record remotely
    response = task_service.record_pr(
        round_number=int(round_number),
        staking_signature=request_data["stakingSignature"],
        staking_key=request_data["stakingKey"],
        pub_key=request_data["pubKey"],
        pr_url=response_data["pr_url"],
        task_id=request_data["taskId"],
        node_type=node_type,
    )
    response_data = response.get("data", {})
    if not response.get("success", False):
        status = response.get("status", 500)
        error = response.get("error", "Unknown error")
        return jsonify({"success": False, "error": error}), status

    return jsonify(
        {
            "success": True,
            "message": response_data["message"],
            "pr_url": response_data["pr_url"],
        }
    )
