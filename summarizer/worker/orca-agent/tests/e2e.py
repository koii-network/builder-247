"""End-to-end test for the summarizer task."""

from pathlib import Path
from prometheus_test import TestRunner
import dotenv
import argparse
import uuid


dotenv.load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser(description="Run summarizer test sequence")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Force reset of all databases before running tests",
    )
    return parser.parse_args()


def add_uuids(db):
    """Post-load callback to process MongoDB data after JSON import"""
    # Process docs collection
    docs = list(db.docs.find({"taskId": runner.config.task_id}))
    for doc in docs:
        if "uuid" not in doc:
            doc["uuid"] = str(uuid.uuid4())
        db.docs.replace_one({"_id": doc["_id"]}, doc)

    # Process summaries collection
    summaries = list(db.summaries.find({"taskId": runner.config.task_id}))
    for summary in summaries:
        if "uuid" not in summary:
            summary["uuid"] = str(uuid.uuid4())
        if "docUuid" not in summary and docs:
            # Link to first doc for simplicity
            summary["docUuid"] = docs[0]["uuid"]
        db.summaries.replace_one({"_id": summary["_id"]}, summary)


# Global reference to the test runner
runner = None


def main():
    global runner
    args = parse_args()

    # Import steps here to avoid circular imports
    from .steps import steps

    # Create test runner with config from YAML
    base_dir = Path(__file__).parent
    runner = TestRunner(
        steps=steps,
        config_file=base_dir / "config.yaml",
        config_overrides={"post_load_callback": add_uuids},
    )

    # Run test sequence
    runner.run(force_reset=args.reset)


if __name__ == "__main__":
    main()
