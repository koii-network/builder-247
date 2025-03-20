"""Audit service module."""

from src.clients import setup_client
from src.workflows.audit.workflow import AuditWorkflow
from src.workflows.audit.prompts import PROMPTS as AUDIT_PROMPTS
from src.utils.logging import log_error
import re
import requests
from github import Github
import os
from typing import Dict, Set
from git import Repo
from src.workflows.utils import verify_pr_signatures
from src.utils.filter_distribution import remove_leaders


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

    Returns:
        bool: True if PR ownership and signature are valid
    """
    try:
        gh = Github(os.environ.get("GITHUB_TOKEN"))

        # Parse PR URL
        match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
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
                "signature": signature,
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
    staking_key: str,
    pub_key: str,
    signature: str,
    distribution_list: Dict[str, Dict[str, str]],
    leader_username: str,
) -> bool:
    """Audit a leader's consolidated PR submission.

    Args:
        task_id: Task ID
        round_number: Round number
        pr_url: URL of the consolidated PR
        repo_owner: Owner of the source repository
        repo_name: Name of the source repository
        staking_key: Leader's staking key
        pub_key: Leader's public key
        signature: Leader's signature
        distribution_list: Pre-filtered dictionary mapping eligible staking keys to reward amounts.
                         This list has already been filtered to only include nodes that:
                         - Have positive rewards
                         - Have valid submissions
                         - Have real PR URLs (not "none")
                         Note: May include leader PRs that need additional filtering
        leader_username: GitHub username of the leader
    """
    try:
        gh = Github(os.environ["GITHUB_TOKEN"])

        # Parse PR URL and get PR object
        match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            log_error(Exception("Invalid PR URL"), context=f"Invalid PR URL: {pr_url}")
            return False

        pr_owner, pr_repo, pr_number = match.groups()

        # Get source repo and PR
        source_repo = gh.get_repo(f"{repo_owner}/{repo_name}")
        pr = source_repo.get_pull(int(pr_number))

        # 1. Verify PR is targeting the source repo's default branch
        if pr.base.repo.owner.login != repo_owner or pr.base.repo.name != repo_name:
            log_error(
                Exception("PR target mismatch"),
                context=f"PR should target {repo_owner}/{repo_name}, got {pr.base.repo.full_name}",
            )
            return False

        # Get source repo's default branch
        if pr.base.ref != source_repo.default_branch:
            log_error(
                Exception("Wrong base branch"),
                context=f"PR should target {source_repo.default_branch}, got {pr.base.ref}",
            )
            return False

        # 2. Verify PR is coming from the leader's fork
        if pr.head.repo.owner.login != leader_username:
            log_error(
                Exception("PR owner mismatch"),
                context=f"PR should come from leader {leader_username}, got {pr.head.repo.owner.login}",
            )
            return False

        # 2. Verify leader's staking key and signature in PR description
        is_valid = verify_pr_signatures(
            pr.body,
            task_id,
            round_number,
            expected_staking_key=staking_key,
            expected_action="merge",
        )
        if not is_valid:
            return False

        # 3. Filter out leader PRs from distribution list
        filtered_distribution_list = remove_leaders(
            distribution_list=distribution_list,
            repo_owner=repo_owner,
            repo_name=repo_name,
        )

        if not filtered_distribution_list:
            log_error(
                Exception("No eligible worker PRs"),
                context="After filtering out leader PRs, no eligible worker PRs remain",
            )
            return True

        # 4. Clone the repository and analyze merge commits
        clone_path = f"/tmp/audit-{repo_owner}-{repo_name}-{pr.head.ref}"
        if os.path.exists(clone_path):
            os.system(f"rm -rf {clone_path}")

        # Clone using the token for auth
        clone_url = f"https://{os.environ['GITHUB_TOKEN']}@github.com/{pr.head.repo.full_name}.git"
        repo = Repo.clone_from(clone_url, clone_path)

        # Checkout the -merged branch
        source_branch = f"task-{task_id}-round-{round_number - 3}"
        merged_branch = f"{source_branch}-merged"
        repo.git.checkout(merged_branch)

        # Get all commits in the PR
        commits = list(repo.iter_commits(f"{pr.base.ref}..{merged_branch}"))

        # 5. Verify all commits are merge commits
        non_merge_commits = [c for c in commits if len(c.parents) != 2]
        if non_merge_commits:
            log_error(
                Exception("Non-merge commits found"),
                context=f"Found {len(non_merge_commits)} non-merge commits",
            )
            return False

        # 6. Verify number of merge commits matches number of PRs in filtered distribution list
        eligible_prs = len(filtered_distribution_list)
        if len(commits) != eligible_prs:
            log_error(
                Exception("Merge commit count mismatch"),
                context=f"Expected {eligible_prs} merge commits, got {len(commits)}",
            )
            return False

        # Track used staking keys to prevent duplicates
        used_staking_keys: Set[str] = set()

        # 7. Verify each merge commit corresponds to a PR from an eligible node
        for commit in commits:
            # Extract branch name and PR URL from merge commit message
            commit_match = re.search(
                r"Merged branch (pr-\d+-[^-]+-[^-]+) for PR (https://github\.com/[^/]+/[^/]+/pull/\d+)",
                commit.message,
            )
            if not commit_match:
                continue

            copied_branch = commit_match.group(1)
            pr_url = commit_match.group(2)

            # Extract PR number from URL
            pr_number = int(pr_url.strip("/").split("/")[-1])
            source_pr = repo.get_pull(int(pr_number))

            # Extract staking key from PR body and verify signature
            for submitter_staking_key in filtered_distribution_list:
                is_valid = verify_pr_signatures(
                    source_pr.body,
                    task_id,
                    round_number - 3,
                    expected_staking_key=submitter_staking_key,
                    expected_action="task",
                )
                if is_valid:
                    # Check for duplicate staking keys
                    if submitter_staking_key in used_staking_keys:
                        log_error(
                            Exception("Duplicate staking key"),
                            context=f"Staking key {submitter_staking_key} used multiple times",
                        )
                        return False

                    used_staking_keys.add(submitter_staking_key)
                    break
            else:
                # No valid signature found for any eligible staking key
                log_error(
                    Exception("Invalid signature"),
                    context=f"No valid signature found in PR #{pr_number} from eligible nodes",
                )
                return False

            # Compare files between original PR and our copied branch before merge
            original_files = set(source_pr.get_files())

            # Get files from our copied branch (state before merge)
            repo.git.checkout(copied_branch)
            copied_files = set(repo.git.ls_files().splitlines())

            # Return to merged branch for next iteration
            repo.git.checkout(merged_branch)

            # Get .gitignore patterns
            gitignore_path = os.path.join(clone_path, ".gitignore")
            ignored_patterns = []
            if os.path.exists(gitignore_path):
                with open(gitignore_path) as f:
                    ignored_patterns = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]

            # Filter out ignored files
            for pattern in ignored_patterns:
                original_files = {f for f in original_files if not re.match(pattern, f)}
                copied_files = {f for f in copied_files if not re.match(pattern, f)}

            if original_files != copied_files:
                log_error(
                    Exception("File mismatch"),
                    context=f"Files in copied branch {copied_branch} don't match original PR #{pr_number}",
                )
                return False

        # 8. Verify all eligible nodes are included
        if used_staking_keys != set(filtered_distribution_list.keys()):
            missing_keys = set(filtered_distribution_list.keys()) - used_staking_keys
            log_error(
                Exception("Missing PRs"),
                context=f"Leader did not include PRs from all eligible nodes. Missing: {missing_keys}",
            )
            return False

        # All checks passed
        return True

    except Exception as e:
        log_error(e, context="Leader audit failed")
        raise

    finally:
        # Cleanup
        if "clone_path" in locals() and os.path.exists(clone_path):
            os.system(f"rm -rf {clone_path}")
