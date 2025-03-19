"""Entry point for todo creator workflow."""

from src.workflows.todocreator.execution import TodoCreatorExecution


def main():
    """Run the todo creator workflow."""
    execution = TodoCreatorExecution()
    execution.start(
        github_token_env_var="GITHUB_TOKEN",
        github_username_env_var="GITHUB_USERNAME",
    )


if __name__ == "__main__":
    main()
