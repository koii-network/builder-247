"""Audit service module."""

from src.clients import setup_client
from src.workflows.audit.workflow import AuditWorkflow
from src.workflows.audit.prompts import PROMPTS as AUDIT_PROMPTS
from src.utils.logging import log_error
import re
import requests
from github import Github
import os
from typing import Dict, Tuple
from git import Repo
from src.workflows.utils import verify_pr_signatures
from src.utils.distribution import validate_distribution_list
import json
from src.tools.github_operations.parser import extract_section


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
    submitter_signature: str,
) -> bool:
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
        submitter_signature: Submitter's signature

    Returns:
        bool: True if PR ownership and signature are valid
    """
    try:
        gh = Github(os.environ.get("GITHUB_TOKEN"))

        # Parse PR URL
        match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            log_error(Exception("Invalid PR URL"), context=f"Invalid PR URL: {pr_url}")
            return False

        owner, repo_name, pr_number = match.groups()

        # Verify repository ownership
        if owner != expected_owner or repo_name != expected_repo:
            log_error(
                Exception("PR URL mismatch"),
                context=f"PR URL mismatch: {pr_url} != {expected_owner}/{expected_repo}",
            )
            return False

        # Get PR and verify author
        repo = gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(int(pr_number))

        if pr.user.login != expected_username:
            log_error(
                Exception("PR username mismatch"),
                context=f"PR username mismatch: {pr.user.login} != {expected_username}",
            )
            return False

        # Verify PR signature
        is_valid = verify_pr_signatures(
            pr.body,
            task_id,
            round_number,
            expected_staking_key=staking_key,
        )
        if not is_valid:
            return False

        # Verify todo assignment with middle server
        response = requests.post(
            os.environ["MIDDLE_SERVER_URL"] + "/api/check-to-do",
            json={
                "stakingKey": staking_key,
                "pubKey": pub_key,
                "roundNumber": round_number,
                "githubUsername": expected_username,
                "prUrl": pr_url,
                "taskId": task_id,
                "signature": submitter_signature,
            },
            headers={"Content-Type": "application/json"},
        )

        response_data = response.json()
        return response_data.get("success", True)

        return True

    except Exception as e:
        log_error(e, context="Error verifying PR ownership")
        return True


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


def audit_leader_submission(
    task_id: str,
    round_number: int,
    pr_url: str,
    repo_owner: str,
    repo_name: str,
    staking_key: str,  # Auditor's staking key
    pub_key: str,  # Auditor's pub key
    staking_signature: str,  # Auditor's staking signature
    public_signature: str,  # Auditor's public signature
    submitter_signature: str,  # Leader's signature
    submitter_staking_key: str,  # Leader's staking key
    submitter_pub_key: str,  # Leader's pub key
    distribution_list: Dict[str, Dict[str, str]],
    leader_username: str,
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
        print(
            f"Distribution list: {json.dumps(distribution_list, indent=2)}", flush=True
        )

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

        # 1. Verify PR is targeting the source repo's default branch
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

        # 2. Verify PR is coming from the leader's fork
        print(
            f"\nVerifying PR owner - expected: {leader_username}, actual: {pr.head.repo.owner.login}",
            flush=True,
        )
        if pr.head.repo.owner.login != leader_username:
            return (
                False,
                f"PR owner mismatch - expected: {leader_username}, got: {pr.head.repo.owner.login}",
            )

        # 2. Verify leader's staking key and signature in PR description
        print("\nVerifying leader's signature...", flush=True)
        is_valid = verify_pr_signatures(
            pr.body,
            task_id,
            round_number,
            expected_staking_key=submitter_staking_key,  # Use leader's key to verify their signature
            expected_action="task",
        )
        if not is_valid:
            return (
                False,
                f"Failed to verify leader's signature for staking key {submitter_staking_key}",
            )

        # 3. Validate and filter distribution list
        print("\nValidating distribution list...", flush=True)
        filtered_distribution_list, error = validate_distribution_list(
            distribution_list=distribution_list,
            repo_owner=repo_owner,
            repo_name=repo_name,
        )
        if error:
            return False, f"Distribution list validation failed: {error}"

        # 4. Clone the repository and analyze merge commits
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
        source_branch = f"task-{task_id}-round-{round_number - 3}"
        merged_branch = f"{source_branch}-merged"
        print(f"Source branch: {source_branch}", flush=True)
        print(f"Merged branch: {merged_branch}", flush=True)
        print(f"Checking out merged branch: {merged_branch}", flush=True)
        repo.git.checkout(merged_branch)

        # Get all commits in the PR
        commits = list(repo.iter_commits(f"{pr.base.ref}..{merged_branch}"))
        print(f"\nFound {len(commits)} commits in PR", flush=True)

        # Get merge commits (for counting against distribution list)
        merge_commits = [c for c in commits if len(c.parents) == 2]
        print(f"Found {len(merge_commits)} merge commits", flush=True)

        # Verify number of merge commits matches number of PRs in filtered distribution list
        eligible_prs = len(filtered_distribution_list)
        print(
            f"\nVerifying merge commit count - expected: {eligible_prs}, actual: {len(merge_commits)}",
            flush=True,
        )
        if len(merge_commits) != eligible_prs:
            return (
                False,
                f"Merge commit count mismatch - expected {eligible_prs}, got {len(merge_commits)}",
            )

        # Track used staking keys to prevent duplicates
        used_staking_keys = set()

        # 7. Verify each merge commit corresponds to a PR from an eligible node
        print("\nVerifying individual merge commits...", flush=True)
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
                    return False, f"No match found in commit message: {commit.message}"

                copied_branch = commit_match.group(1)
                pr_url = commit_match.group(2)
                print(f"Found PR URL: {pr_url}", flush=True)
            except Exception as e:
                return False, f"Error parsing commit message: {str(e)}"

            # Extract PR number from URL
            try:
                print(f"\nExtracting PR details from URL: {pr_url}", flush=True)
                pr_number = int(pr_url.strip("/").split("/")[-1])
                pr_owner = pr_url.split("/")[-4]
                pr_repo_name = pr_url.split("/")[-3]
                print(
                    f"Extracted - owner: {pr_owner}, repo: {pr_repo_name}, number: {pr_number}",
                    flush=True,
                )

                # Get PR using GitHub API
                print(
                    f"Fetching PR from GitHub API: {pr_owner}/{pr_repo_name}#{pr_number}",
                    flush=True,
                )
                gh_repo = gh.get_repo(f"{pr_owner}/{pr_repo_name}")
                source_pr = gh_repo.get_pull(pr_number)
                print(f"Found PR: {source_pr.title}", flush=True)

                # Extract staking key from PR body
                print("Checking PR against filtered distribution list...", flush=True)
                staking_section = extract_section(source_pr.body, "STAKING_KEY")
                if not staking_section:
                    return False, f"No staking key section found in PR #{pr_number}"

                try:
                    pr_staking_key = staking_section.split(":")[0].strip()
                    print(f"Found staking key in PR: {pr_staking_key}", flush=True)
                except Exception as e:
                    return (
                        False,
                        f"Error parsing staking key section in PR #{pr_number}: {str(e)}",
                    )

                # Check if this key is in our filtered distribution list
                if pr_staking_key not in filtered_distribution_list:
                    return (
                        False,
                        f"PR #{pr_number} has staking key {pr_staking_key} not in filtered distribution list",
                    )

                # Check for duplicate staking keys
                if pr_staking_key in used_staking_keys:
                    return False, f"Duplicate staking key found: {pr_staking_key}"

                used_staking_keys.add(pr_staking_key)
                print(
                    f"✓ PR {pr_number} has valid staking key {pr_staking_key}",
                    flush=True,
                )

                # Return to merged branch for next iteration
                print(f"Returning to merged branch {merged_branch}...", flush=True)
                repo.git.checkout(merged_branch)

            except Exception as e:
                return False, f"Error processing PR {pr_url}: {str(e)}"

        # 8. Verify all eligible nodes are included
        print("\nVerifying all eligible nodes are included...")
        print(f"Used staking keys: {used_staking_keys}")
        print(f"Expected staking keys: {set(filtered_distribution_list.keys())}")
        if used_staking_keys != set(filtered_distribution_list.keys()):
            missing_keys = set(filtered_distribution_list.keys()) - used_staking_keys
            return False, f"Missing PRs from nodes: {missing_keys}"

        # 9. Perform code review using the same audit workflow
        print("\nPerforming code review...", flush=True)
        try:
            # Use the auditor's signatures for the review
            is_approved = review_pr(
                pr_url,
                staking_key,  # Auditor's staking key
                pub_key,  # Auditor's pub key
                staking_signature,  # Auditor's staking signature
                public_signature,  # Auditor's public signature
            )
            if not is_approved:
                return False, "PR was rejected during code review"
            print("✓ Code review passed")
        except Exception as e:
            return False, f"Error during code review: {str(e)}"

        # All checks passed
        print("\n✓ All leader audit checks passed!")
        return True, "All leader audit checks passed"

    except Exception as e:
        return False, f"Leader audit failed: {str(e)}"

    finally:
        # Cleanup
        if "clone_path" in locals() and os.path.exists(clone_path):
            os.system(f"rm -rf {clone_path}")
