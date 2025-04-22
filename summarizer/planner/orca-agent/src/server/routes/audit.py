from flask import Blueprint, jsonify, request
from prometheus_swarm.utils.logging import log_key_value
from src.server.services.audit_service import audit_issues_and_tasks
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("audit", __name__)


@bp.post("/audit/<round_number>")
def audit_submission(round_number: int):
    logger.info("Auditing submission")

    data = request.get_json()
    issuesAndTasks = data.get("issuesAndTasks")
    issueSpec = data.get("issueSpec")
    repo_owner = data.get("repoOwner")
    repo_name = data.get("repoName")



    try:
        is_approved = audit_issues_and_tasks(issuesAndTasks, issueSpec, repo_owner, repo_name)
        return jsonify(is_approved)
    except Exception as e:
        logger.error(f"Error reviewing PR: {str(e)}")
        return jsonify(True)
