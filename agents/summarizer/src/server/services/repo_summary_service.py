"""Task service module."""

import requests
import os
from flask import jsonify
from src.database import get_db, Submission
from src.clients import setup_client
from src.workflows.repoSummerizer.workflow import RepoSummerizerWorkflow
from src.utils.logging import logger, log_error
from src.workflows.starRepo.workflow import StarRepoWorkflow
from dotenv import load_dotenv
from src.workflows.repoSummerizer.prompts import PROMPTS
load_dotenv()


def handle_task_creation(task_id, round_number, repo_url):
    """Handle task creation request."""
    try:    
        db = get_db()
        client = setup_client("anthropic")

        workflow = RepoSummerizerWorkflow(
            client=client,
            prompts=PROMPTS,
            repo_url=repo_url,
        )
    
        result = workflow.run()
        if result.get("success"):
            submission = Submission(
                task_id=task_id,
                round_number=round_number,
                status="summarized",
                repo_url=repo_url,
                pr_url=result["data"]["pr_url"],
            )
            db.add(submission)
            db.commit()
            return jsonify({"success": True, "result": result})
        else:
            return jsonify({"success": False, "result": result.get("error", "No result")})
    except Exception as e:
        logger.error(f"Repo summarizer failed: {str(e)}")
        raise


if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    with app.app_context():
        result = handle_task_creation(task_id="1", round_number=6, repo_url="https://github.com/koii-network/builder-test")
        print(result)