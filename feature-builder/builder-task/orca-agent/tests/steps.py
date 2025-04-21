"""Test step definitions."""

from prometheus_test import TestStep
from functools import partial
from .stages import (
    create_repo,
    worker_task,
    worker_submission,
    worker_audit,
    leader_task,
    leader_audit,
    audit_results,
)


steps = [
    TestStep(
        name="create_repo",
        description="Create aggregator repository",
        prepare=create_repo.prepare,
        execute=create_repo.execute,
    ),
    TestStep(
        name="worker1_task",
        description="Execute worker1 task",
        prepare=partial(worker_task.prepare, worker_name="worker1"),
        execute=partial(worker_task.execute, worker_name="worker1"),
    ),
    TestStep(
        name="worker2_task",
        description="Execute worker2 task",
        prepare=partial(worker_task.prepare, worker_name="worker2"),
        execute=partial(worker_task.execute, worker_name="worker2"),
    ),
    TestStep(
        name="worker1_submission",
        description="Get worker1 submission",
        prepare=partial(worker_submission.prepare, worker_name="worker1"),
        execute=worker_submission.execute,
    ),
    TestStep(
        name="worker2_submission",
        description="Get worker2 submission",
        prepare=partial(worker_submission.prepare, worker_name="worker2"),
        execute=worker_submission.execute,
    ),
    TestStep(
        name="worker1_audit",
        description="Worker1 audits Worker2",
        prepare=partial(
            worker_audit.prepare, auditor_name="worker1", target_name="worker2"
        ),
        execute=partial(worker_audit.execute, auditor_name="worker1"),
    ),
    TestStep(
        name="worker2_audit",
        description="Worker2 audits Worker1",
        prepare=partial(
            worker_audit.prepare, auditor_name="worker2", target_name="worker1"
        ),
        execute=partial(worker_audit.execute, auditor_name="worker2"),
    ),
    TestStep(
        name="worker_audit_results",
        description="Update worker audit results",
        prepare=partial(audit_results.prepare, role="worker"),
        execute=audit_results.execute,
    ),
    TestStep(
        name="leader_task",
        description="Execute leader task",
        prepare=leader_task.prepare,
        execute=leader_task.execute,
    ),
    TestStep(
        name="leader_submission",
        description="Get leader submission",
        prepare=partial(worker_submission.prepare, worker_name="leader"),
        execute=worker_submission.execute,
    ),
    TestStep(
        name="leader_audit",
        description="Execute leader audit",
        prepare=leader_audit.prepare,
        execute=leader_audit.execute,
    ),
    TestStep(
        name="leader_audit_results",
        description="Update leader audit results",
        prepare=partial(audit_results.prepare, role="leader"),
        execute=audit_results.execute,
    ),
]
