"""Workflow exceptions module."""


class WorkflowError(Exception):
    """Base error class for workflow errors."""

    def __init__(self, reason: str, details: str):
        self.reason = reason
        self.details = details
        super().__init__(f"{reason}: {details}")
