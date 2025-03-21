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
import re
load_dotenv()


def handle_task_creation(task_id, round_number, signature, staking_key, pub_key, starOnly=True):
    """Handle task creation request."""
    try:    
        db = get_db()
        client = setup_client("anthropic")
        # Convert GitHub web URL to raw content URL
        readmeUrl = "https://raw.githubusercontent.com/koii-network/prometheus-swarm-bounties/master/README.md"
        # read this readme
        readme = requests.get(readmeUrl).text
        
        # Extract all GitHub URLs using regex
        github_pattern = r'https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-_]+/?'
        github_urls = re.findall(github_pattern, readme)
        
        # Remove any duplicates
        github_urls = list(set(github_urls))
        print(f"Found {len(github_urls)} GitHub repositories:")
        for url in github_urls:
            print(url)
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
        
        # Convert the list of URLs to a dictionary
        repo_urls_dict = {"urls": github_urls}

        submission = Submission(
            task_id=task_id,
            round_number=round_number,
            status="stared",
            repo_urls=repo_urls_dict
        )
        db.add(submission)
        db.commit()
        if starOnly:
            return jsonify({"success": True, "result": "Repository starred"})
        else:
            workflow = RepoSummerizerWorkflow(
                client=client,
                prompts=PROMPTS,
                repo_url="https://github.com/koii-network/namespace-wrapper",
            )
    
            result = workflow.run()
            if result.get("success"):
                submission.status = "summarized"
                submission.pr_url = result.data.get("pr_url")
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
        result = handle_task_creation(task_id="1", round_number=6, signature="1", staking_key="1", pub_key="1", starOnly=False)
        print(result)