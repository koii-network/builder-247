"""Test step definitions."""

from prometheus_test import TestStep
from functools import partial
from .stages import (
    worker_task,
    worker_submission,
    worker_audit,
    audit_results,
)


steps = [
    TestStep(
        name="worker_task",
        description="Execute worker task",
        prepare=worker_task.prepare,
        execute=worker_task.execute,
        worker="worker",
    ),
    TestStep(
        name="worker_submission",
        description="Submit worker task",
        prepare=worker_submission.prepare,
        execute=worker_submission.execute,
        worker="worker1",
    ),
    TestStep(
        name="worker_audit",
        description="Worker2 audits Worker1",
        prepare=partial(worker_audit.prepare, target_name="worker1"),
        execute=worker_audit.execute,
        worker="worker2",
    ),
    TestStep(
        name="audit_results",
        description="Update audit results",
        prepare=partial(audit_results.prepare, role="worker"),
        execute=audit_results.execute,
        worker="worker1",
    ),
]
