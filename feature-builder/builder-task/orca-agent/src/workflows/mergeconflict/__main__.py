"""Entry point for merge conflict workflow."""

from src.workflows.mergeconflict.execution import MergeConflictExecution


def main():
    """Run the merge conflict workflow."""
    execution = MergeConflictExecution()
    execution.start(
        github_token_env_var="GITHUB_TOKEN",
        github_username_env_var="GITHUB_USERNAME",
    )


if __name__ == "__main__":
    main()
