"""Test step definitions."""

from prometheus_test import TestStep
from functools import partial
from .stages import (
    create_repo,
    record_repo,
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
        worker="leader",
    ),
    TestStep(
        name="record_repo",
        description="Record aggregator repository",
        prepare=record_repo.prepare,
        execute=record_repo.execute,
        worker="leader",
    ),
    TestStep(
        name="worker1_task",
        description="Execute worker1 task",
        prepare=worker_task.prepare,
        execute=worker_task.execute,
        worker="worker1",
    ),
    TestStep(
        name="worker2_task",
        description="Execute worker2 task",
        prepare=worker_task.prepare,
        execute=worker_task.execute,
        worker="worker2",
    ),
    TestStep(
        name="worker1_submission",
        description="Get worker1 submission",
        prepare=worker_submission.prepare,
        execute=worker_submission.execute,
        worker="worker1",
    ),
    TestStep(
        name="worker2_submission",
        description="Get worker2 submission",
        prepare=worker_submission.prepare,
        execute=worker_submission.execute,
        worker="worker2",
    ),
    TestStep(
        name="worker1_audit",
        description="Worker1 audits Worker2",
        prepare=partial(worker_audit.prepare, target_name="worker2"),
        execute=worker_audit.execute,
        worker="worker1",
    ),
    TestStep(
        name="worker2_audit",
        description="Worker2 audits Worker1",
        prepare=partial(worker_audit.prepare, target_name="worker1"),
        execute=worker_audit.execute,
        worker="worker2",
    ),
    TestStep(
        name="worker_audit_results",
        description="Update worker audit results",
        prepare=partial(audit_results.prepare, role="worker"),
        execute=audit_results.execute,
        worker="worker1",
    ),
    TestStep(
        name="leader_task",
        description="Execute leader task",
        prepare=leader_task.prepare,
        execute=leader_task.execute,
        worker="leader",
    ),
    TestStep(
        name="leader_submission",
        description="Get leader submission",
        prepare=worker_submission.prepare,
        execute=worker_submission.execute,
        worker="leader",
    ),
    TestStep(
        name="leader_audit",
        description="Execute leader audit",
        prepare=leader_audit.prepare,
        execute=leader_audit.execute,
        worker="worker1",
    ),
    TestStep(
        name="leader_audit_results",
        description="Update leader audit results",
        prepare=partial(audit_results.prepare, role="leader"),
        execute=audit_results.execute,
        worker="leader",
    ),
]
