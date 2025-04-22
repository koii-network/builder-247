"""Test step definitions."""

from prometheus_test import TestStep
from functools import partial
from .stages import (
    validate_api_keys,
    validate_github,
    fetch_summarizer_todo,
    generate_summary,
    submit_summary,
    audit_summary,
)

steps = [
    TestStep(
        name="validate_api_keys",
        description="Validate Anthropic API key",
        prepare=validate_api_keys.prepare,
        execute=validate_api_keys.execute,
        worker="worker1",
    ),
    TestStep(
        name="validate_github",
        description="Validate GitHub credentials",
        prepare=validate_github.prepare,
        execute=validate_github.execute,
        worker="worker1",
    ),
    TestStep(
        name="fetch_todo_worker1",
        description="Fetch summarizer todo for worker1",
        prepare=fetch_summarizer_todo.prepare,
        execute=fetch_summarizer_todo.execute,
        worker="worker1",
    ),
    TestStep(
        name="fetch_todo_worker2",
        description="Fetch summarizer todo for worker2",
        prepare=fetch_summarizer_todo.prepare,
        execute=fetch_summarizer_todo.execute,
        worker="worker2",
    ),
    TestStep(
        name="generate_summary_worker1",
        description="Generate summary for worker1's todo",
        prepare=generate_summary.prepare,
        execute=generate_summary.execute,
        worker="worker1",
    ),
    TestStep(
        name="generate_summary_worker2",
        description="Generate summary for worker2's todo",
        prepare=generate_summary.prepare,
        execute=generate_summary.execute,
        worker="worker2",
    ),
    TestStep(
        name="submit_summary_worker1",
        description="Submit summary for worker1",
        prepare=submit_summary.prepare,
        execute=submit_summary.execute,
        worker="worker1",
    ),
    TestStep(
        name="submit_summary_worker2",
        description="Submit summary for worker2",
        prepare=submit_summary.prepare,
        execute=submit_summary.execute,
        worker="worker2",
    ),
    TestStep(
        name="audit_worker1",
        description="Worker1 audits Worker2's submission",
        prepare=partial(audit_summary.prepare, target_name="worker2"),
        execute=audit_summary.execute,
        worker="worker1",
    ),
    TestStep(
        name="audit_worker2",
        description="Worker2 audits Worker1's submission",
        prepare=partial(audit_summary.prepare, target_name="worker1"),
        execute=audit_summary.execute,
        worker="worker2",
    ),
]
