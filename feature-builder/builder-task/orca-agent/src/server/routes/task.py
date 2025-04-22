from flask import Blueprint, jsonify, request
from src.server.services import task_service
from prometheus_swarm.utils.logging import logger
import requests
import os

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

    # Create the aggregator repo (which now handles assign_issue internally)
    result = task_service.create_aggregator_repo(task_id)
    print(f"result: {result}")

    # Extract status code from result if present, default to 200
    status_code = result.pop("status", 200) if isinstance(result, dict) else 200
    return jsonify(result), status_code


@bp.post("/add-aggregator-info/<task_id>")
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
    if node_type not in ["worker", "leader"]:
        return jsonify({"success": False, "message": "Invalid node type"}), 400

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
        "addPRSignature",
    ]

    if any(request_data.get(field) is None for field in required_fields):
        missing_fields = [
            field for field in required_fields if request_data.get(field) is None
        ]
        logger.error(f"Missing required fields: {missing_fields}")
        return (
            jsonify({"success": False, "message": f"Missing data: {missing_fields}"}),
            401,
        )

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
        return jsonify({"success": False, "message": error}), status

    logger.info(response_data["message"])

    # Record PR for both worker and leader tasks, but only workers record remotely
    response = task_service.record_pr(
        round_number=int(round_number),
        staking_signature=request_data["addPRSignature"],
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
        return jsonify({"success": False, "message": error}), status

    return jsonify(
        {
            "success": True,
            "message": response_data["message"],
            "pr_url": response_data["pr_url"],
        }
    )


@bp.post("/update-audit-result/<task_id>/<round_number>")
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
