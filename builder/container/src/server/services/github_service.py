import re
import requests
from github import Github
import os
import logging

logger = logging.getLogger(__name__)


def verify_pr_ownership(
    pr_url, expected_username, expected_owner, expected_repo, signature, staking_key
):
    try:
        gh = Github(os.environ.get("GITHUB_TOKEN"))

        match = re.match(r"https://github.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
        if not match:
            return False

        owner, repo_name, pr_number = match.groups()

        if owner != expected_owner or repo_name != expected_repo:
            return False

        repo = gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(int(pr_number))

        if pr.user.login != expected_username:
            return False

        response = requests.post(
            os.environ.get("MIDDLE_SERVER_URL") + "/api/check-to-do",
            json={
                "prUrl": pr_url,
                "signature": signature,
                "pubKey": staking_key,
                "github_username": expected_username,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()["is_valid"]

    except Exception as e:
        logger.error(f"Error verifying PR ownership: {str(e)}")
        return False
