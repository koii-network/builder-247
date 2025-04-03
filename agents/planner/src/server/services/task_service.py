"""Task service module."""

import requests
import os
from flask import jsonify
from src.database import get_db, Submission
from src.clients import setup_client
from src.workflows.todocreator.workflow import TodoCreatorWorkflow
from src.workflows.todocreator.prompts import PROMPTS
from src.utils.logging import logger, log_error
from dotenv import load_dotenv

load_dotenv()


def handle_task_creation(repo_url, issue_spec):
    """Handle task creation request."""
    workflow = TodoCreatorWorkflow(
        client=setup_client("anthropic"),
        prompts=PROMPTS,
        repo_url=repo_url,
        issue_spec=issue_spec,
    )
    result = workflow.run()
    if not result or not result.get("success"):
        log_error(Exception(result.get("error", "No result")), "Task creation failed")
        return jsonify({"success": False, "error": result.get("error", "No result")})
    return jsonify({"success": True, "data": result.get("data", {})})
    



