# """Audit service module."""

# import logging
# from src.clients import setup_client
# from src.workflows.audit.workflow import AuditWorkflow
# from src.workflows.audit.prompts import PROMPTS as AUDIT_PROMPTS

# logger = logging.getLogger(__name__)


# def review_pr(pr_url):
#     """Review PR and decide if it should be accepted, revised, or rejected."""
#     try:
#         # Set up client and workflow
#         client = setup_client("anthropic")
#         workflow = AuditWorkflow(
#             client=client,
#             prompts=AUDIT_PROMPTS,
#             pr_url=pr_url,
#         )

#         # Run workflow and get result
#         workflow.run()
#         return True
#     except Exception as e:
#         logger.error(f"PR review failed: {str(e)}")
#         raise Exception("PR review failed")
