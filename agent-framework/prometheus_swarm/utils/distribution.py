"""Distribution list filtering utilities."""

import re
from typing import Dict, Tuple
from github import Github
import os
from prometheus_swarm.workflows.utils import verify_pr_signatures
from prometheus_swarm.tools.github_operations.parser import extract_section


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
    gh = Github(os.environ.get("GITHUB_TOKEN"))
    target_repo = gh.get_repo(f"{repo_owner}/{repo_name}")
    # Get parent's owner if it exists (repo is a fork), otherwise use repo's owner
    upstream_owner = getattr(target_repo.parent, "owner", target_repo.owner).login
    print(f"Upstream repo owner: {upstream_owner}")

    for node_key, node_data in distribution_list.items():
        try:
            # Skip if no PR URL or dummy PR
            pr_url = node_data.get("prUrl")
            print(f"\nChecking PR for {node_key}: {pr_url}")

            if not pr_url or not isinstance(pr_url, str):
                print(f"Invalid PR URL for {node_key}")
                continue

            # Skip if PR URL is "none" or empty
            if pr_url.lower() == "none" or not pr_url.strip():
                print(f"Empty PR URL for {node_key}")
                continue

            # Parse PR URL to check if it's a leader PR
            pr_match = re.match(
                r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url.strip()
            )
            if not pr_match:
                print(f"PR URL format invalid for {node_key}: {pr_url}")
                continue

            pr_owner = pr_match.group(1)
            print(f"PR owner: {pr_owner}, upstream: {upstream_owner}")

            # If PR was made to upstream repo, it's a leader PR - skip it
            if pr_owner == upstream_owner:
                print(f"Skipping leader PR from {node_key}")
                continue

            # Include this node in filtered list
            filtered_distribution_list[node_key] = node_data

        except Exception as e:
            print(f"Error processing {node_key}: {str(e)}")
            continue

    print(f"Filtered {len(distribution_list)} PRs to {len(filtered_distribution_list)}")
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
        - filtered_list: Distribution list with leader PRs removed and signatures validated
        - error_message: Error message if validation failed, None if successful
    """
    if not distribution_list:
        return None, "Missing or empty distribution list"

    print(f"\nValidating {len(distribution_list)} PRs...")

    try:
        # First filter out leader PRs
        filtered_list = remove_leaders(
            distribution_list=distribution_list,
            repo_owner=repo_owner,
            repo_name=repo_name,
        )

        if not filtered_list:
            return None, "No eligible worker PRs after filtering leaders"

        # Now validate signatures in each PR
        gh = Github(os.environ.get("GITHUB_TOKEN"))
        validated_list = {}

        for node_key, node_data in filtered_list.items():
            try:
                pr_url = node_data["prUrl"]
                task_id = node_data["taskId"]
                round_number = node_data["roundNumber"]
                staking_key = node_data["stakingKey"]

                print(f"\nValidating PR: {pr_url}")
                print(f"Expected staking key: {staking_key}")

                # Parse PR URL and get PR
                match = re.match(
                    r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url
                )
                if not match:
                    print(f"Invalid PR URL format: {pr_url}")
                    continue

                pr_owner, pr_repo, pr_number = match.groups()
                repo = gh.get_repo(f"{pr_owner}/{pr_repo}")
                pr = repo.get_pull(int(pr_number))

                # First extract the actual staking key from the PR
                staking_section = extract_section(pr.body, "STAKING_KEY")
                if not staking_section:
                    print(f"No staking key section found in PR #{pr_number}")
                    continue

                try:
                    pr_staking_key = staking_section.split(":")[0].strip()
                    print(f"Found staking key in PR: {pr_staking_key}")
                except Exception as e:
                    print(f"Error parsing staking key section: {str(e)}")
                    continue

                # Verify the PR's staking key matches the one in distribution list
                if pr_staking_key != staking_key:
                    print(
                        f"Staking key mismatch - PR: {pr_staking_key}, Expected: {staking_key}"
                    )
                    continue

                # Now verify the signature
                print(f"Verifying signature for key: {staking_key}")
                is_valid = verify_pr_signatures(
                    pr.body,
                    task_id,
                    round_number,
                    expected_staking_key=staking_key,
                    expected_action="task",
                )

                if is_valid:
                    print(f"✓ Valid signature found for {staking_key}")
                    validated_list[staking_key] = node_data
                else:
                    print(f"✗ Invalid signature for {staking_key}")

            except Exception as e:
                print(f"Error validating PR for {node_key}: {str(e)}")
                continue

        if not validated_list:
            return None, "No PRs with valid signatures found"

        print(f"\nValidated {len(validated_list)} PRs with valid signatures")
        return validated_list, None

    except Exception as e:
        print(f"Error in validate_distribution_list: {str(e)}")
        return None, f"Error validating distribution list: {str(e)}"
