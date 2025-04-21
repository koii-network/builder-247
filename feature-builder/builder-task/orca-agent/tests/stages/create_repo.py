"""Stage for creating the aggregator repository."""

import requests


def prepare(runner):
    """Prepare data for creating a repository"""
    return {
        "taskId": runner.config.task_id,
        "roundNumber": runner.round_number,
        "action": "create-repo",
    }


def execute(runner, data):
    """Execute repository creation step"""
    worker = runner.get_worker("leader")
    url = f"{worker.url}/create-aggregator-repo/{data['taskId']}"
    response = requests.post(url, json=data)
    result = response.json()

    if result.get("success"):
        runner.state["fork_url"] = result["data"]["fork_url"]
        runner.state["issue_uuid"] = result["data"]["issue_uuid"]

    return result
