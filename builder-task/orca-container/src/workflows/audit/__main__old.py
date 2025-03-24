import sys
import argparse
from src.workflows.audit.workflow import AuditWorkflow
from src.utils.logging import configure_logging, log_error
from src.clients import setup_client
from src.workflows.audit.prompts import PROMPTS


def run_workflow(pr_url):
    client = setup_client("anthropic")
    workflow = AuditWorkflow(
        client=client,
        prompts=PROMPTS,
        pr_url=pr_url,
    )
    workflow.run()


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run audit workflow on a pull request")
    parser.add_argument(
        "--pr-url", type=str, help="URL of the pull request to audit", required=True
    )
    parser.add_argument(
        "--model",
        type=str,
        default="anthropic",
        choices=["anthropic", "openai", "xai"],
        help="Model provider to use (default: anthropic)",
    )
    args = parser.parse_args()

    try:
        # Set up logging
        configure_logging()

        # Review pull request
        run_workflow(args.pr_url)

    except Exception as e:
        log_error(e, "Script failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
