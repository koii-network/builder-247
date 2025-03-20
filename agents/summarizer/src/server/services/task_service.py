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
import re
load_dotenv()


def handle_task_creation():
    """Handle task creation request."""
    try:    

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

        workflow = RepoSummerizerWorkflow(
            client=client,
            prompts=PROMPTS,
            repo_url=github_urls[0],
        )

        result = workflow.run()

        return jsonify({"success": True, "result": result})
  

    except Exception as e:
        logger.error(f"Repo summarizer failed: {str(e)}")
        raise


if __name__ == "__main__":
    handle_task_creation()