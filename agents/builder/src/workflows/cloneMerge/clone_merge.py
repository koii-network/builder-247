"""Merge conflict resolver workflow implementation."""

import os
import time
from github import Github
from src.workflows.base import Workflow
from src.utils.logging import log_section, log_key_value, log_error
from src.workflows.mergeconflict import phases
from src.tools.git_operations.implementations import (
    add_remote,
)
from src.workflows.utils import (
    check_required_env_vars,
    validate_github_auth,
    setup_repo_directory,
    setup_git_user_config,
    cleanup_repo_directory,
    get_current_files,
    clone_repository,
)

from src.tools.github_operations.implementations import (
    create_pull_request,
    get_pull_request_info,

    fork_repository,
)
example_pr_url = "https://github.com/koii-network/prometheus-beta/pull/5943"
example_repo_full_name = "koii-network/prometheus-beta"
example_new_name_base = "koii-network_prometheus-beta"

example_owner_2 = "rhonrhon06"
example_new_name_head = "rhonrhon06_prometheus-beta"
example_head_url = "https://github.com/rhonrhon06/prometheus-beta"
example_pr_number = 5943
example_submitter_full_name = "rhonrhon06/prometheus-beta"
if __name__ == "__main__":
    """Set up repository and workspace."""

    pr_info = get_pull_request_info(example_repo_full_name, example_pr_number)
    print("pr_info", pr_info)
    head_branch = pr_info["data"]["head"]
    base_branch = pr_info["data"]["base"]
    print("head_branch", head_branch)
    print("base_branch", base_branch)
    repo_path_head, original_dir_head = setup_repo_directory()
    fork_result = fork_repository(example_repo_full_name, repo_path_head)
    add_remote(name=example_owner_2, url=example_head_url)
    
    # make a new pr from the forked repo
    repo_full_name_my_head = f"HermanL02/{example_new_name_head}"
    repo_full_name_my_base = f"HermanL02/{example_new_name_base}"
    pr_result = create_pull_request(
        repo_full_name=repo_full_name_my_head,
        target_repo_full_name=repo_full_name_my_base,
        title="New Pull Request Title",
        head=head_branch,
        description="This is a description of the pull request.",
        tests=["Test 1", "Test 2"],
        todo="Complete the merge process",
        acceptance_criteria="All tests pass and code is reviewed",
        base=base_branch
    )

    
    print("pr_result", pr_result)       
