"""Audit workflow execution."""

from prometheus_swarm.workflows.base import WorkflowExecution
from src.workflows.audit.workflow import AuditWorkflow
from src.workflows.audit.prompts import PROMPTS
from typing import List


class AuditExecution(WorkflowExecution):
    def __init__(self):
        super().__init__(
            description="Run audit workflow on a pull request",
            additional_arguments={
                "pr-url": {
                    "type": str,
                    "help": "URL of the pull request to audit",
                    "required": True,
                },
            },
            prompts=PROMPTS,
        )

    def _setup(
        self,
        github_token_env_var: str = "GITHUB_TOKEN",
        github_username_env_var: str = "GITHUB_USERNAME",
        required_env_vars: List[str] = None,
        **kwargs,
    ):
        """Set up audit workflow context.

        Args:
            github_token_env_var: Name of env var containing GitHub token
            github_username_env_var: Name of env var containing GitHub username
            required_env_vars: Additional required environment variables
        """
        # Combine GitHub env vars with any additional required vars
        env_vars = [github_token_env_var, github_username_env_var]
        if required_env_vars:
            env_vars.extend(required_env_vars)

        super()._setup(required_env_vars=env_vars)

        # Add task ID, round number, and signatures to context
        self._add_signature_context(
            additional_payload={
                "pr_url": self.args.pr_url,
                "action": "audit",
            }
        )

        # Create workflow instance
        self.workflow = AuditWorkflow(
            client=self.client,
            prompts=self.prompts,
            pr_url=self.args.pr_url,
            staking_key=self.context["staking_key"],
            pub_key=self.context["pub_key"],
            staking_signature=self.context["staking_signature"],
            public_signature=self.context["public_signature"],
            github_token=github_token_env_var,
            github_username=github_username_env_var,
        )

    def _run(self, **kwargs):
        """Run the audit workflow."""
        result = self.workflow.run()

        if result is None:
            raise Exception("Audit workflow failed")

        return result
