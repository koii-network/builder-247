import sys
from src.workflows.audit.workflow import AuditWorkflow
from src.utils.logging import configure_logging, log_error
from src.clients import setup_client
from src.workflows.prompts import AUDIT_PROMPTS


def run_workflow(pr_url):
    client = setup_client("anthropic")
    workflow = AuditWorkflow(
        client=client,
        prompts=AUDIT_PROMPTS,
        pr_url=pr_url,
    )
    workflow.run()


if __name__ == "__main__":
    try:
        # Set up logging
        configure_logging()

        # Get command line arguments
        if len(sys.argv) < 2:
            print("Usage: python3 -m src.workflows.audit <pr_url>")
            sys.exit(1)
        pr_url = sys.argv[1]

        # Review pull request
        run_workflow(pr_url)

    except Exception as e:
        log_error(e, "Script failed")
        sys.exit(1)
