"""Task service module."""

from flask import jsonify
from prometheus_swarm.clients import setup_client
from src.workflows.repoClassifier.workflow import RepoClassifierWorkflow
from prometheus_swarm.utils.logging import logger
from dotenv import load_dotenv
from src.workflows.repoClassifier.prompts import PROMPTS

load_dotenv()


def handle_task_creation(repo_url):
    """Handle task creation request."""
    try:
        client = setup_client("anthropic")

        workflow = RepoClassifierWorkflow(
            client=client,
            prompts=PROMPTS,
            repo_url=repo_url,
        )
        result = workflow.run()
        if result.get("success"):
            return result
        else:
            return jsonify(
                {"success": False, "result": result.get("error", "No result")}
            )
    except Exception as e:
        logger.error(f"Repo classification failed: {str(e)}")
        return jsonify({"success": False, "message": str(e)})


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    with app.app_context():
        result = handle_task_creation(
            repo_url="https://github.com/koii-network/builder-test",
        )
        print(result)
