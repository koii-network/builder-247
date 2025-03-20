"""Task service module."""

import requests
import os
from flask import jsonify
from src.database import get_db, Submission
from src.clients import setup_client
from src.workflows.repoSummerizer.workflow import RepoSummerizerWorkflow
from src.utils.logging import logger, log_error
from dotenv import load_dotenv
from src.workflows.repoSummerizer.prompts import PROMPTS
load_dotenv()


def handle_task_creation(repo_url):
    """Handle task creation request."""
    try:    

        client = setup_client("anthropic")
        workflow = RepoSummerizerWorkflow(
            client=client,
            prompts=PROMPTS,
            repo_url=repo_url,
        )

        result = workflow.run()

        return jsonify({"success": True, "result": result})
  

    except Exception as e:
        logger.error(f"PR creation failed: {str(e)}")
        if "db" in locals():
            # Update submission status
            submission = (
                db.query(Submission)
                .filter(Submission.round_number == round_number)
                .first()
            )
            if submission:
                submission.status = "failed"
                db.commit()
                logger.info(f"Updated status to failed for round {round_number}")
        raise


