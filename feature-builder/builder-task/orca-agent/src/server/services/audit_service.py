"""Audit service module."""

from prometheus_swarm.clients import setup_client
from src.workflows.audit.workflow import AuditWorkflow
from src.workflows.audit.prompts import PROMPTS as AUDIT_PROMPTS
from prometheus_swarm.utils.logging import log_error
import re
import requests
from github import Github
import os
from git import Repo
from typing import Tuple, Dict
from prometheus_swarm.tools.github_operations.parser import extract_section
from src.workflows.utils import verify_pr_signatures
import json


def verify_pr_ownership(
    pr_url: str,
    expected_username: str,
    uuid: str,
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

    response = requests.get(
        os.environ["MIDDLE_SERVER_URL"]
        + f"/api/builder/get-source-repo/{node_type}/{uuid}",
        headers={"Content-Type": "application/json"},
    )

    response_data = response.json()
    if not response_data.get("success"):
        log_error(
            Exception("Failed to get source repo"),
            context=f"Failed to get source repo: {response_data.get('message')}",
        )
        return {
            "valid": False,
            "pr_list": {},
        }

    data = response_data.get("data", {})
    expected_owner = data.get("repoOwner")
    expected_repo = data.get("repoName")

    if not expected_owner or not expected_repo:
        log_error(
            Exception("Missing repo info"),
            context="Missing repoOwner or repoName in response",
        )
        return {
            "valid": False,
            "pr_list": {},
        }

    print("\n=== VERIFY PR OWNERSHIP ===")
    print(f"PR URL: {pr_url}")
    print(f"Expected username: {expected_username}")
    print(f"Expected owner/repo: {expected_owner}/{expected_repo}")
    print(f"Task ID: {task_id}")
    print(f"Round number: {round_number}")
    print(f"Node type: {node_type}")
    print(f"Staking key: {staking_key[:10]}...")
    print(f"Pub key: {pub_key[:10]}...")
    print(f"Signature: {signature[:20]}...")

    try:
        node_actions = {
            "worker": "fetch-todo",
            "leader": "fetch-issue",
        }

        node_endpoints = {
            "worker": "check-to-do",
            "leader": "check-issue",
        }

        print(f"Node action: {node_actions.get(node_type)}")
        print(f"Node endpoint: {node_endpoints.get(node_type)}")

        gh = Github(os.environ.get("GITHUB_TOKEN"))

        # Parse PR URL
        match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            log_error(Exception("Invalid PR URL"), context=f"Invalid PR URL: {pr_url}")
            print("Invalid PR URL format")
            print("=== END VERIFY PR OWNERSHIP (FAILED: Invalid PR URL) ===\n")
            return {
                "valid": False,
                "pr_list": {},
            }

        owner, repo_name, pr_number = match.groups()
        print(f"Parsed PR: owner={owner}, repo={repo_name}, number={pr_number}")

        # Verify repository ownership
        if owner != expected_owner or repo_name != expected_repo:
            log_error(
                Exception("PR URL mismatch"),
                context=f"PR URL mismatch: {pr_url} != {expected_owner}/{expected_repo}",
            )
            print(
                f"Repository mismatch: {owner}/{repo_name} vs {expected_owner}/{expected_repo}"
            )
            print("=== END VERIFY PR OWNERSHIP (FAILED: Repository mismatch) ===\n")
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
            print(f"Username mismatch: {pr.user.login} vs {expected_username}")
            print("=== END VERIFY PR OWNERSHIP (FAILED: Username mismatch) ===\n")
            return {
                "valid": False,
                "pr_list": {},
            }

        print("Verifying PR signature...")
        # Verify PR signature
        is_valid = verify_pr_signatures(
            pr.body,
            task_id,
            round_number,
            expected_staking_key=staking_key,
            expected_action=node_actions[node_type],
        )
        print(f"PR signature verification result: {is_valid}")

        if not is_valid:
            print("=== END VERIFY PR OWNERSHIP (FAILED: Invalid signature) ===\n")
            return {
                "valid": False,
                "pr_list": {},
            }

        # Verify todo assignment with middle server
        print("Verifying with middle server...")
        middleware_payload = {
            "stakingKey": staking_key,
            "pubKey": pub_key,
            "roundNumber": round_number,
            "githubUsername": expected_username,
            "prUrl": pr_url,
            "taskId": task_id,
            "signature": signature,
        }
        print(f"Middleware payload: {json.dumps(middleware_payload, indent=2)}")

        middleware_url = (
            os.environ["MIDDLE_SERVER_URL"]
            + f"/api/builder/{node_endpoints[node_type]}"
        )
        print(f"Middleware URL: {middleware_url}")

        response = requests.post(
            middleware_url,
            json=middleware_payload,
            headers={"Content-Type": "application/json"},
        )

        response_data = response.json()
        print(f"Middleware response: {json.dumps(response_data, indent=2)}")

        result = {
            "valid": response_data.get("success", True),
            "pr_list": response_data.get("data", {}).get("pr_list", {}),
            "issue_uuid": response_data.get("data", {}).get("issue_uuid", None),
        }

        print(f"Final result: {json.dumps(result, indent=2)}")
        print("=== END VERIFY PR OWNERSHIP ===\n")
        return result

    except Exception as e:
        log_error(e, context="Error verifying PR ownership")
        print(f"Exception: {str(e)}")
        print("=== END VERIFY PR OWNERSHIP (FAILED: Exception) ===\n")
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
    leader_username: str,
    pr_list: Dict[str, list[str]],
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
        total_prs = sum(len(urls) for urls in pr_list.values())
        print(
            f"PR list contains {total_prs} PRs from {len(pr_list)} staking keys",
            flush=True,
        )

        # Track processed merge commits to ensure all are valid
        valid_commits = 0

        # Track used PR URLs to prevent duplicates
        used_pr_urls = set()

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
                    expected_pr_urls = pr_list[worker_staking_key]
                    if merge_pr_url.strip() not in [
                        url.strip() for url in expected_pr_urls
                    ]:
                        print(
                            f"Warning: PR URL not found in list for staking key {worker_staking_key}"
                        )
                        print(f"  Expected one of: {expected_pr_urls}")
                        print(f"  Found: {merge_pr_url}")
                        continue

                    # Check for duplicate PR URLs
                    if merge_pr_url in used_pr_urls:
                        print(f"Warning: Duplicate PR URL: {merge_pr_url}")
                        continue

                    used_pr_urls.add(merge_pr_url)
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
        print(f"PR list contained {total_prs} PRs from {len(pr_list)} staking keys")

        # Check if we have enough valid commits
        if valid_commits == 0:
            return False, "No valid PRs found in merge commits"

        # Require all PRs from the PR list to be merged
        if valid_commits < total_prs:
            missing_count = total_prs - valid_commits
            missing_prs = []
            for staking_key, urls in pr_list.items():
                for url in urls:
                    if url not in used_pr_urls:
                        missing_prs.append(f"{url} ({staking_key})")
            missing_prs_display = ", ".join(missing_prs[:5])
            if len(missing_prs) > 5:
                missing_prs_display += " and more"
            return (
                False,
                f"{missing_count} PRs from the PR list were not found in merge commits: {missing_prs_display}",
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
