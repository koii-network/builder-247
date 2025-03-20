"""Distribution list filtering utilities."""

import re
from github import Github
from typing import Dict, Tuple
from src.utils.logging import log_key_value, log_value
import json


def remove_leaders(
    distribution_list: Dict[str, Dict[str, str]],
    repo_owner: str,
    repo_name: str,
) -> Dict[str, Dict[str, str]]:
    """Filter out leader PRs from distribution list.

    A PR is considered a leader PR if it was made directly to the upstream repo.
    """
    filtered_distribution_list = {}

    # Get source repo and its upstream
    gh = Github()
    source_repo = gh.get_repo(f"{repo_owner}/{repo_name}")
    if not source_repo.fork:
        raise ValueError("Source repo is not a fork")
    else:
        # Get the upstream repo
        upstream_owner = source_repo.parent.owner.login

    log_key_value("Upstream repo owner", upstream_owner)

    for node_key, node_data in distribution_list.items():
        try:
            # Skip if no PR URL or dummy PR
            pr_url = node_data.get("prUrl")

            # Parse PR URL to check if it's a leader PR
            pr_match = re.match(
                r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url
            )
            if not pr_match:
                log_value("PR URL is not a valid GitHub PR URL")
                continue

            pr_owner = pr_match.groups()[0]

            # If PR was made to upstream repo, it's a leader PR - skip it
            if pr_owner == upstream_owner:
                log_value(f"Skipping leader PR from node {node_key}")
                continue

            # Include this node in filtered list
            filtered_distribution_list[node_key] = node_data

        except Exception as e:
            log_value(f"Error checking PR for node {node_key}: {str(e)}")
            continue

    orig_count = len(distribution_list)
    filtered_count = len(filtered_distribution_list)
    log_value(
        f"Filtered distribution list from {orig_count} to {filtered_count} nodes after removing leader PRs",
    )

    return filtered_distribution_list


def validate_distribution_list(
    distribution_list: Dict[str, Dict[str, str]],
    repo_owner: str,
    repo_name: str,
) -> Tuple[Dict[str, Dict[str, str]], str]:
    """Validate and filter distribution list.

    Args:
        distribution_list: Raw distribution list from request
        repo_owner: Owner of the repository
        repo_name: Name of the repository

    Returns:
        tuple: (filtered_list, error_message)
        - filtered_list: Distribution list with leader PRs removed
        - error_message: Error message if validation failed, None if successful
    """
    if not distribution_list:
        return None, "Missing or empty distribution list"

    # Debug distribution list
    print("\nOriginal distribution list:")
    print(json.dumps(distribution_list, indent=2))

    try:
        # Filter out leader PRs from distribution list
        filtered_distribution_list = remove_leaders(
            distribution_list=distribution_list,
            repo_owner=repo_owner,
            repo_name=repo_name,
        )

        print("\nFiltered distribution list (after removing leaders):")
        print(json.dumps(filtered_distribution_list, indent=2))

        if not filtered_distribution_list:
            return None, "No eligible worker PRs after filtering leaders"

        return filtered_distribution_list, None

    except Exception as e:
        return None, f"Error validating distribution list: {str(e)}"
