"""Stage for creating the aggregator repository."""

import requests


def prepare(runner, worker):
    """Prepare data for creating a repository"""
    return {
        "taskId": runner.config.task_id,
        "roundNumber": runner.current_round,
        "action": "create-repo",
    }


def execute(runner, worker, data):
    """Execute repository creation step"""
    url = f"{worker.url}/create-aggregator-repo/{data['taskId']}"
    response = requests.post(url, json=data)
    result = response.json()

    if result.get("success"):
        runner.state["fork_url"] = result["data"]["fork_url"]
        runner.state["issue_uuid"] = result["data"]["issue_uuid"]
        runner.state["branch_name"] = result["data"]["branch_name"]

    return result
