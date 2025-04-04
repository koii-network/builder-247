"""Audit service module."""

from agent_framework.clients import setup_client
from src.workflows.audit.workflow import AuditWorkflow
from src.workflows.audit.prompts import PROMPTS as AUDIT_PROMPTS
from agent_framework.utils.logging import log_error
import re
import requests
from github import Github
import os
from git import Repo
from typing import Tuple, Dict
from agent_framework.tools.github_operations.parser import extract_section
from src.workflows.utils import verify_pr_signatures


def verify_pr_ownership(
    pr_url: str,
    expected_username: str,
    expected_owner: str,
    expected_repo: str,
    task_id: str,
    round_number: int,
    staking_key: str,
    pub_key: str,
    signature: str,
    node_type: str,
) -> Dict[str, bool | Dict[str, str]]:
    """Verify PR ownership and signature.

    Args:
        pr_url: URL of the PR to verify
        expected_username: Expected GitHub username of PR author
        expected_owner: Expected owner of the repository
        expected_repo: Expected repository name
        task_id: Task ID for signature validation
        round_number: Round number for signature validation
        staking_key: Worker's staking key
        pub_key: Worker's public key
        signature: Submitter's signature
        node_type: Type of node (worker or leader)
    Returns:
        bool: True if PR ownership and signature are valid
    """
    try:
        node_actions = {
            "worker": "fetch-todo",
            "leader": "fetch-issue",
        }

        node_endpoints = {
            "worker": "check-to-do",
            "leader": "check-issue",
        }

        gh = Github(os.environ.get("GITHUB_TOKEN"))

        # Parse PR URL
        match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            log_error(Exception("Invalid PR URL"), context=f"Invalid PR URL: {pr_url}")
            return {
                "valid": False,
                "pr_list": {},
            }

        owner, repo_name, pr_number = match.groups()

        # Verify repository ownership
        if owner != expected_owner or repo_name != expected_repo:
            log_error(
                Exception("PR URL mismatch"),
                context=f"PR URL mismatch: {pr_url} != {expected_owner}/{expected_repo}",
            )
            return {
                "valid": False,
                "pr_list": {},
            }

        # Get PR and verify author
        repo = gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(int(pr_number))

        if pr.user.login != expected_username:
            log_error(
                Exception("PR username mismatch"),
                context=f"PR username mismatch: {pr.user.login} != {expected_username}",
            )
            return {
                "valid": False,
                "pr_list": {},
            }

        # Verify PR signature
        is_valid = verify_pr_signatures(
            pr.body,
            task_id,
            round_number,
            expected_staking_key=staking_key,
            expected_action=node_actions[node_type],
        )
        if not is_valid:
            return {
                "valid": False,
                "pr_list": {},
            }

        # Verify todo assignment with middle server
        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + f"/api/{node_endpoints[node_type]}",
            json={
                "stakingKey": staking_key,
                "pubKey": pub_key,
                "roundNumber": round_number,
                "githubUsername": expected_username,
                "prUrl": pr_url,
                "taskId": task_id,
                "signature": signature,
            },
            headers={"Content-Type": "application/json"},
        )

        response_data = response.json()
        return {
            "valid": response_data.get("success", True),
            "pr_list": response_data.get("data", {}).get("pr_list", {}),
        }

    except Exception as e:
        log_error(e, context="Error verifying PR ownership")
        return {
            "valid": False,
            "pr_list": {},
        }


def review_pr(pr_url, staking_key, pub_key, staking_signature, public_signature):
    """Review PR and decide if it should be accepted, revised, or rejected."""
    try:
        # Set up client and workflow
        client = setup_client("anthropic")
        workflow = AuditWorkflow(
            client=client,
            prompts=AUDIT_PROMPTS,
            pr_url=pr_url,
            staking_key=staking_key,
            pub_key=pub_key,
            staking_signature=staking_signature,
            public_signature=public_signature,
        )

        # Run workflow and get result
        workflow.run()
        return True
    except Exception as e:
        log_error(e, context="PR review failed")
        raise Exception("PR review failed")


def validate_pr_list(
    pr_url: str,
    repo_owner: str,
    repo_name: str,
    staking_key: str,  # Auditor's staking key
    pub_key: str,  # Auditor's pub key
    staking_signature: str,  # Auditor's staking signature
    public_signature: str,  # Auditor's public signature
    submitter_staking_key: str,  # Leader's staking key
    leader_username: str,
    pr_list: Dict[str, str],
    issue_uuid: str,
) -> Tuple[bool, str]:
    """Audit a leader's consolidated PR submission.

    Returns:
        Tuple[bool, str]: (passed, error_message)
        - passed: True if audit passed, False otherwise
        - error_message: Description of why audit failed, or success message
    """
    try:
        print("\nStarting leader audit...", flush=True)
        print(f"PR URL: {pr_url}", flush=True)
        print(f"Leader username: {leader_username}", flush=True)
        print(f"Leader staking key: {submitter_staking_key}", flush=True)

        gh = Github(os.environ["GITHUB_TOKEN"])

        # Parse PR URL and get PR object
        match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            return False, f"Invalid PR URL format: {pr_url}"

        pr_owner, pr_repo, pr_number = match.groups()
        print(
            f"\nPR details - owner: {pr_owner}, repo: {pr_repo}, number: {pr_number}",
            flush=True,
        )

        # Get source repo and PR
        source_repo = gh.get_repo(f"{repo_owner}/{repo_name}")
        pr = source_repo.get_pull(int(pr_number))
        print(f"PR base repo: {pr.base.repo.full_name}", flush=True)
        print(f"PR head repo: {pr.head.repo.full_name}", flush=True)

        # Verify PR is targeting the source repo's default branch
        if pr.base.repo.owner.login != repo_owner or pr.base.repo.name != repo_name:
            return (
                False,
                f"PR target mismatch - expected: {repo_owner}/{repo_name}, got: {pr.base.repo.full_name}",
            )

        # Get source repo's default branch
        if pr.base.ref != source_repo.default_branch:
            return (
                False,
                f"Wrong base branch - expected: {source_repo.default_branch}, got: {pr.base.ref}",
            )

        # Verify PR is coming from the leader's fork
        print(
            f"\nVerifying PR owner - expected: {leader_username}, actual: {pr.head.repo.owner.login}",
            flush=True,
        )
        if pr.head.repo.owner.login != leader_username:
            return (
                False,
                f"PR owner mismatch - expected: {leader_username}, got: {pr.head.repo.owner.login}",
            )

        # Clone the repository and analyze merge commits
        clone_path = f"/tmp/audit-{repo_owner}-{repo_name}-{pr.head.ref}"
        print(f"\nClone path: {clone_path}", flush=True)
        if os.path.exists(clone_path):
            print("Removing existing clone path", flush=True)
            os.system(f"rm -rf {clone_path}")

        # Clone using the token for auth
        clone_url = f"https://{os.environ['GITHUB_TOKEN']}@github.com/{pr.head.repo.full_name}.git"
        print(f"\nCloning repository from {pr.head.repo.full_name}...", flush=True)
        print(
            f"Clone URL: {clone_url.replace(os.environ['GITHUB_TOKEN'], 'TOKEN')}",
            flush=True,
        )
        repo = Repo.clone_from(clone_url, clone_path)

        # Checkout the -merged branch
        source_branch = issue_uuid
        merged_branch = f"{source_branch}-merged"
        print(f"Source branch: {source_branch}", flush=True)
        print(f"Merged branch: {merged_branch}", flush=True)
        print(f"Checking out merged branch: {merged_branch}", flush=True)
        repo.git.checkout(merged_branch)

        # Get all commits in the PR
        commits = list(repo.iter_commits(f"{pr.base.ref}..{merged_branch}"))
        print(f"\nFound {len(commits)} commits in PR", flush=True)

        # Get merge commits
        merge_commits = [c for c in commits if len(c.parents) == 2]
        print(f"Found {len(merge_commits)} merge commits", flush=True)

        # 7. Verify merge commits against PR list
        print("\nVerifying merge commits against PR list...", flush=True)
        print(f"PR list contains {len(pr_list)} PRs", flush=True)

        # Track processed merge commits to ensure all are valid
        valid_commits = 0

        # Track used staking keys to prevent duplicates
        used_staking_keys = set()

        # Verify each merge commit corresponds to a PR from the PR list
        for commit in merge_commits:
            print(f"\nChecking commit: {commit.hexsha[:8]}", flush=True)
            print(f"Commit message: {commit.message}", flush=True)

            # Extract branch name and PR URL from merge commit message
            try:
                commit_match = re.search(
                    r"Merged branch (pr-\d+[^\"]+) for PR (https://github\.com/[^/]+/[^/]+/pull/\d+)",
                    commit.message,
                )
                if not commit_match:
                    print(
                        f"Warning: No match found in commit message: {commit.message}"
                    )
                    continue

                copied_branch = commit_match.group(1)
                merge_pr_url = commit_match.group(2)
                print(f"Found PR URL in commit: {merge_pr_url}", flush=True)

                # Extract PR number from URL
                try:
                    pr_match = re.match(
                        r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", merge_pr_url
                    )
                    if not pr_match:
                        print(
                            f"Warning: Invalid PR URL format in commit: {merge_pr_url}"
                        )
                        continue

                    pr_owner, pr_repo_name, pr_number = pr_match.groups()

                    # Fetch the PR to extract the staking key from its description
                    pr_repo = gh.get_repo(f"{pr_owner}/{pr_repo_name}")
                    worker_pr = pr_repo.get_pull(int(pr_number))

                    # Extract staking key from PR body
                    staking_section = extract_section(worker_pr.body, "STAKING_KEY")
                    if not staking_section:
                        print(
                            f"Warning: No staking key section found in PR #{pr_number}"
                        )
                        continue

                    worker_staking_key = staking_section.split(":")[0].strip()
                    print(f"Found staking key in PR: {worker_staking_key}")

                    # Check if this staking key is in our PR list
                    if worker_staking_key not in pr_list:
                        print(
                            f"Warning: Staking key {worker_staking_key} not found in PR list"
                        )
                        continue

                    # Verify the PR URL matches what's in our PR list
                    expected_pr_url = pr_list[worker_staking_key]
                    if expected_pr_url.strip() != merge_pr_url.strip():
                        print(
                            f"Warning: PR URL mismatch for staking key {worker_staking_key}"
                        )
                        print(f"  Expected: {expected_pr_url}")
                        print(f"  Found: {merge_pr_url}")
                        continue

                    # Check for duplicate staking keys
                    if worker_staking_key in used_staking_keys:
                        print(
                            f"Warning: Duplicate PR from staking key {worker_staking_key}"
                        )
                        continue

                    used_staking_keys.add(worker_staking_key)
                    valid_commits += 1
                    print(f"✓ Valid PR from staking key {worker_staking_key}")

                except Exception as e:
                    print(f"Warning: Error processing PR {merge_pr_url}: {str(e)}")
                    continue

            except Exception as e:
                print(f"Warning: Error parsing commit message: {str(e)}")
                continue

        print(
            f"\nFound {valid_commits} valid merge commits out of {len(merge_commits)}"
        )
        print(f"PR list contained {len(pr_list)} entries")

        # Check if we have enough valid commits
        if valid_commits == 0:
            return False, "No valid PRs found in merge commits"

        # We don't require all PRs to be merged, so just warn if counts don't match
        if valid_commits < len(pr_list):
            print(
                f"Warning: {len(pr_list) - valid_commits} PRs from the PR list were not found in merge commits"
            )

        # All checks passed
        print("\n✓ All leader audit checks passed!")
        return True, "All leader audit checks passed"

    except Exception as e:
        return False, f"Leader audit failed: {str(e)}"

    finally:
        # Cleanup
        if "clone_path" in locals() and os.path.exists(clone_path):
            os.system(f"rm -rf {clone_path}")
