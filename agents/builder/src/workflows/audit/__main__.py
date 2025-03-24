"""Entry point for audit workflow."""

from agents.builder.src.workflows.audit.test import AuditExecution


def main():
    """Run the audit workflow."""
    execution = AuditExecution()
    execution.start(
        github_token_env_var="GITHUB_TOKEN",
        github_username_env_var="GITHUB_USERNAME",
    )


if __name__ == "__main__":
    main()
