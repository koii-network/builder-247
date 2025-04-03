"""Entry point for task workflow."""

from agents.builder.src.workflows.task.test import TaskExecution


def main():
    """Run the task workflow."""
    execution = TaskExecution()
    execution.start(
        leader_token_env_var="LEADER_GITHUB_TOKEN",
        leader_username_env_var="LEADER_GITHUB_USERNAME",
        worker_token_env_var="WORKER_GITHUB_TOKEN",
        worker_username_env_var="WORKER_GITHUB_USERNAME",
    )


if __name__ == "__main__":
    main()
