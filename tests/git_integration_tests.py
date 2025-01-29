
from src.tools.git import GitAutomation
example_repo = "https://github.com/koii-network/docs.git"
original_owner = "koii-network"
owner = "HermanL02"
repo = "docs"
fork_url = "https://github.com/HermanL02/docs.git"
example_branch_name = "new-feature-branch"
def test_fork_repo():
    git_automation = GitAutomation(git_dir="./")
    assert git_automation.fork_repo(example_repo) is True

def test_check_fork_exists():
    git_automation = GitAutomation(git_dir="./")
    assert git_automation.check_fork_exists(owner, repo) is True

def test_clone_repo():
    git_automation = GitAutomation(git_dir="./")
    assert git_automation.clone_repo(example_repo) is True

def test_checkout_new_branch():
    git_automation = GitAutomation(git_dir="./")
    assert git_automation.checkout_new_branch(example_branch_name) is True

def test_commit_and_push():
    git_automation = GitAutomation(git_dir="./")
    assert git_automation.commit_and_push() is True

def test_create_pr():
    git_automation = GitAutomation(git_dir="./")
    assert git_automation.create_pr(original_owner, owner, repo, base_branch="main", head_branch=example_branch_name, title="Sync changes") is True

def test_sync_fork():
    git_automation = GitAutomation(git_dir="./")
    assert git_automation.sync_fork(example_repo, fork_url) is True

if __name__ == "__main__":
    # test_fork_repo()
    test_check_fork_exists()
    # test_clone_repo()
    # test_checkout_new_branch()
    # test_commit_and_push()
    # test_create_pr()
    # test_sync_fork()