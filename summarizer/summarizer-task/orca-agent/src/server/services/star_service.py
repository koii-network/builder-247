"""Task service module."""

import requests
import os
from flask import jsonify
from prometheus_swarm.database import get_db 
from prometheus_swarm.clients import setup_client
from src.workflows.repoSummarizer.workflow import RepoSummarizerWorkflow
from prometheus_swarm.utils.logging import logger, log_error
from src.workflows.starRepo.workflow import StarRepoWorkflow
from dotenv import load_dotenv
from src.workflows.repoSummarizer.prompts import PROMPTS

load_dotenv()


def handle_star_task(task_id, round_number, github_urls):
    """Handle task creation request."""
    try:
        db = get_db()
        client = setup_client("anthropic")
        for url in github_urls:
            star_workflow = StarRepoWorkflow(
                client=client,
                prompts=PROMPTS,
                repo_url=url,
            )
            star_result = star_workflow.run()
            if not star_result or not star_result.get("success"):
                log_error(
                    Exception(star_result.get("error", "No result")),
                    "Repository star failed",
                )
        return jsonify({"success": True, "result": "Repository starred"})
    except Exception as e:
        logger.error(f"Repo summarizer failed: {str(e)}")
        raise


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    with app.app_context():
        result = handle_star_task(
            task_id="1",
            round_number=6,
            github_urls=["https://github.com/koii-network/builder-test"],
        )
        print(result)
