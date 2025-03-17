"""Distribution list filtering utilities."""

import os
import re
import requests
from github import Github
from typing import Dict, Tuple
from src.utils.logging import log_key_value


def filter_leader_prs(
    distribution_list: Dict[str, float],
    task_id: str,
    round_number: int,
    repo_owner: str,
    repo_name: str,
    github_client: Github,
) -> Tuple[Dict[str, float], str]:
    """Filter out leader PRs from distribution list.

    Args:
        distribution_list: Dictionary mapping staking keys to reward amounts
        task_id: Task ID for fetching PR info
        round_number: Round number for fetching PR info
        repo_owner: Owner of the source repository
        repo_name: Name of the source repository
        github_client: Initialized Github client

    Returns:
        Tuple containing:
        - Filtered distribution list with only worker PRs
        - Default branch name of the source repository
    """
    filtered_distribution_list = {}
    source_repo = github_client.get_repo(f"{repo_owner}/{repo_name}")
    default_branch = source_repo.default_branch

    for node_key, amount in distribution_list.items():
        try:
            # For each node in distribution list, check their PR
            response = requests.get(
                os.environ["MIDDLE_SERVER_URL"] + "/api/check-to-do",
                json={
                    "stakingKey": node_key,
                    "roundNumber": round_number,
                    "taskId": task_id,
                },
                headers={"Content-Type": "application/json"},
            )
            todo_data = response.json()
            if not todo_data.get("success"):
                continue

            pr_url = todo_data.get("data", {}).get("prUrl")
            if not pr_url:
                continue

            # Parse PR URL to check if it's a leader PR
            pr_match = re.match(
                r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url
            )
            if not pr_match:
                continue

            pr_owner, pr_repo, pr_num = pr_match.groups()
            pr_repo = github_client.get_repo(f"{pr_owner}/{pr_repo}")
            node_pr = pr_repo.get_pull(int(pr_num))

            # Skip if PR targets default branch of original repo (leader PR)
            if (
                node_pr.base.repo.full_name == f"{repo_owner}/{repo_name}"
                and node_pr.base.ref == default_branch
            ):
                log_key_value("Filtering", f"Skipping leader PR from node {node_key}")
                continue

            # Include this node in filtered list
            filtered_distribution_list[node_key] = amount

        except Exception as e:
            log_key_value("Error", f"Error checking PR for node {node_key}: {str(e)}")
            continue

    orig_count = len(distribution_list)
    filtered_count = len(filtered_distribution_list)
    log_key_value(
        "Filtering",
        f"Filtered distribution list from {orig_count} to {filtered_count} nodes after removing leader PRs",
    )

    return filtered_distribution_list, default_branch
