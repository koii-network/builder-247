"""Audit workflow execution."""

import os
from src.workflows.base import WorkflowExecution
from src.workflows.audit.workflow import AuditWorkflow
from src.workflows.audit.prompts import PROMPTS


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

    def _setup(self):
        """Set up audit workflow context."""
        required_env_vars = ["GITHUB_TOKEN", "GITHUB_USERNAME"]
        super()._setup(required_env_vars=required_env_vars)

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
            github_token=os.environ["GITHUB_TOKEN"],
            github_username=os.environ["GITHUB_USERNAME"],
        )

    def _run(self):
        """Run the audit workflow."""
        result = self.workflow.run()

        if result is None:
            raise Exception("Audit workflow failed")

        return result
