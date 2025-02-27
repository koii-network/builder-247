import sys
from pathlib import Path
import csv
import json
from src.workflows.task.workflow import TaskWorkflow
from src.utils.logging import (
    log_section,
    log_key_value,
    configure_logging,
)
from src.database import get_db, Log
from src.clients import setup_client
from src.workflows.prompts import TASK_PROMPTS


def run_workflow(repo_owner, repo_name, todo, acceptance_criteria):
    client = setup_client("anthropic")
    workflow = TaskWorkflow(
        client=client,
        prompts=TASK_PROMPTS,
        repo_owner=repo_owner,
        repo_name=repo_name,
        todo=todo,
        acceptance_criteria=acceptance_criteria,
    )
    workflow.run()


if __name__ == "__main__":
    try:
        # Set up logging
        configure_logging()

        todos_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "data"
            / "test_todos.csv"
        )

        if not todos_path.exists():
            db = get_db()
            log = Log(level="ERROR", message=f"Todos file not found at {todos_path}")
            db.add(log)
            db.commit()
            sys.exit(1)

        with open(todos_path, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for i, row in enumerate(reader):
                if len(row) >= 2:
                    todo, acceptance_criteria = row[0], row[1]
                    try:

                        log_section(f"PROCESSING TODO {i}")
                        run_workflow(
                            repo_owner="koii-network",
                            repo_name="builder-test",
                            todo=todo.strip(),
                            acceptance_criteria=acceptance_criteria.strip(),
                        )
                    except Exception as e:
                        db = get_db()
                        log = Log(
                            level="ERROR",
                            message=str(e),
                            additional_data=json.dumps({"todo_index": i}),
                        )
                        db.add(log)
                        db.commit()
                        sys.exit(1)
                else:
                    log_key_value("Skipping invalid row", row)
    except Exception as e:
        db = get_db()
        log = Log(level="ERROR", message=str(e))
        db.add(log)
        db.commit()
        sys.exit(1)
