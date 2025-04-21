from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypedDict
import json
from contextlib import contextmanager
from pymongo import MongoClient
from .workers import TestEnvironment
import yaml
import os


class MongoCollectionConfig(TypedDict, total=False):
    data_file: str  # Optional, not all collections need data files
    required_count: int


class MongoConfig(TypedDict, total=False):
    database: str
    collections: Dict[str, MongoCollectionConfig]


@dataclass
class TestConfig:
    """Configuration for the test runner"""

    base_dir: Path = Path.cwd()
    data_dir: Optional[Path] = None
    workers_config: str = "workers.json"
    task_id: str = "test-task-123"
    base_port: int = 5000
    server_entrypoint: Optional[Path] = None
    max_rounds: Optional[int] = None  # Will be calculated from number of todos
    post_load_callback: Optional[Callable[[Any], None]] = (
        None  # Callback for post-JSON data processing
    )
    mongodb: MongoConfig = field(
        default_factory=lambda: {
            "database": "builder247",
            "collections": {
                "issues": {"required_count": 1},
                "todos": {"required_count": 1},
                "systemprompts": {"required_count": 0},
                "audits": {"required_count": 0},
            },
        }
    )

    @classmethod
    def from_yaml(
        cls, yaml_path: Path, base_dir: Optional[Path] = None
    ) -> "TestConfig":
        """Create TestConfig from a YAML file"""
        # Load YAML config
        with open(yaml_path) as f:
            config = yaml.safe_load(f) or {}

        # Use base_dir from argument or yaml_path's parent
        base_dir = base_dir or yaml_path.parent
        config["base_dir"] = base_dir

        # Convert relative paths to absolute
        if "data_dir" in config:
            config["data_dir"] = base_dir / config["data_dir"]
        if "server_entrypoint" in config:
            config["server_entrypoint"] = base_dir / config["server_entrypoint"]

        # Merge MongoDB config with defaults
        if "mongodb" in config:
            default_mongodb = cls().mongodb
            mongodb_config = config["mongodb"]

            # Use default database if not specified
            if "database" not in mongodb_config:
                mongodb_config["database"] = default_mongodb["database"]

            # Merge collection configs with defaults
            if "collections" in mongodb_config:
                for coll_name, default_coll in default_mongodb["collections"].items():
                    if coll_name not in mongodb_config["collections"]:
                        mongodb_config["collections"][coll_name] = default_coll
                    else:
                        # Merge with default collection config
                        mongodb_config["collections"][coll_name] = {
                            **default_coll,
                            **mongodb_config["collections"][coll_name],
                        }

        # Create instance with YAML values, falling back to defaults
        return cls(**{k: v for k, v in config.items() if k in cls.__dataclass_fields__})

    def __post_init__(self):
        # Convert string paths to Path objects
        self.base_dir = Path(self.base_dir)
        if self.data_dir:
            self.data_dir = Path(self.data_dir)
        else:
            self.data_dir = self.base_dir / "data"

        if self.server_entrypoint:
            self.server_entrypoint = Path(self.server_entrypoint)


@dataclass
class TestStep:
    """Represents a single step in a task test sequence"""

    name: str
    description: str
    worker: str
    prepare: Callable[[], Dict[str, Any]]  # Returns data needed for the step
    execute: Callable[Dict[str, Any], Any]  # Takes prepared data and executes step
    validate: Optional[Callable[[Any, Any], None]] = (
        None  # Optional validation function
    )


class TestRunner:
    """Main test runner that executes a sequence of test steps"""

    def __init__(
        self,
        steps: List[TestStep],
        config_file: Optional[Path] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
    ):
        """Initialize test runner with steps and optional config"""
        self.steps = steps
        self.config = TestConfig.from_yaml(config_file) if config_file else TestConfig()

        # Apply any config overrides
        if config_overrides:
            for key, value in config_overrides.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    raise ValueError(f"Invalid config override: {key}")

        # Initialize state
        self.state = {}
        self.current_round = 1
        self.last_completed_step = None

        # Ensure directories exist
        self.config.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize test environment and MongoDB client
        self._test_env = None
        self._mongo_client = None
        self._max_rounds = None

    @property
    def mongo_client(self) -> MongoClient:
        """Get MongoDB client, initializing if needed"""
        if self._mongo_client is None:
            # Get MongoDB URI from environment variable
            mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            self._mongo_client = MongoClient(mongodb_uri)
        return self._mongo_client

    @property
    def max_rounds(self) -> int:
        """Get maximum number of rounds, calculating from todos if not specified"""
        if self._max_rounds is None:
            if self.config.max_rounds is not None:
                self._max_rounds = self.config.max_rounds
            else:
                # Count todos and add 1
                db = self.mongo_client[self.config.mongodb["database"]]
                self._max_rounds = (
                    db.todos.count_documents({"taskId": self.config.task_id}) + 1
                )
        return self._max_rounds

    def check_mongodb_state(self) -> bool:
        """Check if MongoDB is in the expected state

        Returns:
            bool: True if all collections exist and have required document counts
        """
        db = self.mongo_client[self.config.mongodb["database"]]

        for coll_name, coll_config in self.config.mongodb["collections"].items():
            # Skip if collection doesn't exist and no documents required
            if coll_config.get("required_count", 0) == 0:
                continue

            # Check if collection exists and has required documents
            if coll_name not in db.list_collection_names():
                print(f"Collection {coll_name} does not exist")
                return False

            count = db[coll_name].count_documents({"taskId": self.config.task_id})
            if count < coll_config["required_count"]:
                print(
                    f"Collection {coll_name} has {count} documents, requires {coll_config['required_count']}"
                )
                return False

        return True

    def reset_local_databases(self):
        """Reset all local database files"""
        print("\nResetting local databases...")
        for worker in self.test_env.workers.values():
            if worker.database_path.exists():
                print(f"Deleting database file: {worker.database_path}")
                worker.database_path.unlink()

    def reset_mongodb(self):
        """Reset MongoDB database and import data files from config"""
        print("\nResetting MongoDB database...")

        # Connect to MongoDB
        db = self.mongo_client[self.config.mongodb["database"]]

        # Clear collections
        print("\nClearing collections...")
        for collection in self.config.mongodb["collections"]:
            db[collection].delete_many({})

        # Import data files
        for coll_name, coll_config in self.config.mongodb["collections"].items():
            if "data_file" not in coll_config:
                continue

            data_file = self.config.data_dir / coll_config["data_file"]
            if not data_file.exists():
                if coll_config.get("required_count", 0) > 0:
                    raise FileNotFoundError(
                        f"Required data file not found: {data_file}"
                    )
                continue

            print(f"Importing data for {coll_name} from {data_file}")
            with open(data_file) as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]

                # Add task_id to all documents
                for item in data:
                    item["taskId"] = self.config.task_id

                # Insert data into collection
                db[coll_name].insert_many(data)

        # Run post-load callback if provided
        if self.config.post_load_callback:
            print("\nRunning post-load data processing...")
            self.config.post_load_callback(db)

        # Reset max_rounds cache after data import
        self._max_rounds = None

    def ensure_clean_state(self, force_reset: bool = False):
        """Ensure databases are in a clean state

        Args:
            force_reset: If True, always reset databases regardless of current state
        """
        needs_reset = force_reset or not self.check_mongodb_state()

        if needs_reset:
            print("\nResetting databases...")
            self.reset_local_databases()
            self.reset_mongodb()
            self.reset_state()

    @property
    def test_env(self) -> TestEnvironment:
        """Get the test environment, initializing if needed"""
        if self._test_env is None:
            workers_config = Path(self.config.workers_config)
            if not workers_config.is_absolute():
                workers_config = self.config.base_dir / workers_config

            self._test_env = TestEnvironment(
                config_file=workers_config,
                base_dir=self.config.base_dir,
                base_port=self.config.base_port,
                server_entrypoint=self.config.server_entrypoint,
            )
        return self._test_env

    def get_worker(self, name: str):
        """Get a worker by name"""
        return self.test_env.get_worker(name)

    def save_state(self):
        """Save current test state to file"""
        state_file = self.config.data_dir / "test_state.json"
        # Add current round and step to state before saving
        self.state["current_round"] = self.current_round
        if self.last_completed_step:
            self.state["last_completed_step"] = self.last_completed_step
        with open(state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def load_state(self):
        """Load test state from file if it exists"""
        state_file = self.config.data_dir / "test_state.json"
        if state_file.exists():
            with open(state_file, "r") as f:
                self.state = json.load(f)
                # Restore current round and step from state
                self.current_round = self.state.get("current_round", 1)
                self.last_completed_step = self.state.get("last_completed_step")

    def reset_state(self):
        """Clear the current state"""
        self.state = {
            "rounds": {},
            "current_round": self.current_round,
        }
        self.last_completed_step = None
        state_file = self.config.data_dir / "test_state.json"
        if state_file.exists():
            state_file.unlink()

    def log_step(self, step: TestStep):
        """Log test step execution"""
        print("\n" + "#" * 80)
        print(f"STEP {step.name}: {step.description}")
        print("#" * 80)

    @contextmanager
    def run_environment(self):
        """Context manager for running the test environment"""
        with self.test_env:
            try:
                self.load_state()
                yield
            finally:
                self.save_state()

    def next_round(self):
        """Move to next round"""
        self.current_round += 1
        # Initialize state for new round if needed
        if "rounds" not in self.state:
            self.state["rounds"] = {}
        if str(self.current_round) not in self.state["rounds"]:
            self.state["rounds"][str(self.current_round)] = {}
        self.state["current_round"] = self.current_round
        self.last_completed_step = None

    def run(self, force_reset=False):
        """Run the test sequence."""
        # Ensure clean state before starting
        self.ensure_clean_state(force_reset)

        with self.run_environment():
            while self.current_round <= self.max_rounds:
                round_steps = [s for s in self.steps]

                # Find the index to start from based on last completed step
                start_index = 0
                if self.last_completed_step:
                    for i, step in enumerate(round_steps):
                        if step.name == self.last_completed_step:
                            start_index = i + 1
                            break

                # Skip already completed steps
                for step in round_steps[start_index:]:
                    self.log_step(step)

                    worker = self.get_worker(step.worker)
                    # Prepare step data
                    data = step.prepare(self, worker)

                    # Execute step
                    result = step.execute(self, worker, data)

                    # Check for errors
                    if not result.get("success"):
                        error_msg = result.get("error", "Unknown error")
                        raise RuntimeError(f"Step {step.name} failed: {error_msg}")

                    # Validate step result if validation function exists
                    if step.validate:
                        step.validate(self, result)

                    # Save state after successful step
                    self.last_completed_step = step.name
                    self.save_state()

                # Move to next round after completing all steps
                if self.current_round < self.max_rounds:
                    self.next_round()
