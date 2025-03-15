from flask import Blueprint, jsonify, request
from src.server.services import task_service
from src.utils.logging import logger

bp = Blueprint("task", __name__)


@bp.post("/worker-task/<round_number>")
def start_worker_task(round_number):
    return start_task(round_number, "worker", request)


@bp.post("/leader-task/<round_number>")
def start_leader_task(round_number):
    return start_task(round_number, "leader", request)


@bp.post("/create-aggregator-repo/<round_number>")
def create_aggregator_repo(round_number):
    request_data = request.get_json()
    required_fields = [
        "taskId",
        "repoOwner",
        "repoName",
    ]
    if any(request_data.get(field) is None for field in required_fields):
        return jsonify({"error": "Missing data"}), 401
    return task_service.create_aggregator_repo(
        round_number,
        request_data["taskId"],
        request_data["repoOwner"],
        request_data["repoName"],
    )


def start_task(round_number, node_type, request):
    if node_type not in ["worker", "leader"]:
        return jsonify({"error": "Invalid node type"}), 400

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
        "distributionList",
        "repoOwner",
        "repoName",
    ]
    if any(request_data.get(field) is None for field in required_fields):
        return jsonify({"error": "Missing data"}), 401

    response = task_functions[node_type](
        task_id=request_data["taskId"],
        round_number=int(round_number),
        staking_signature=request_data["stakingSignature"],
        staking_key=request_data["stakingKey"],
        public_signature=request_data["publicSignature"],
        pub_key=request_data["pubKey"],
        repo_owner=request_data["repoOwner"],
        repo_name=request_data["repoName"],
        distribution_list=request_data["distributionList"],
    )
    response_data = response.get("data", {})
    if not response.get("success", False):
        status = response.get("status", 500)
        error = response.get("error", "Unknown error")
        return jsonify({"error": error}), status

    logger.info(response_data["message"])

    response = task_service.record_pr(
        round_number=int(round_number),
        staking_signature=request_data["stakingSignature"],
        staking_key=request_data["stakingKey"],
        pub_key=request_data["pubKey"],
        pr_url=response_data["pr_url"],
    )
    response_data = response.get("data", {})
    if response.get("success", False):
        return jsonify({"message": response_data["message"]})
    else:
        status = response.get("status", 500)
        error = response.get("error", "Unknown error")
        return jsonify({"error": error}), status
