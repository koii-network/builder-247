# Prometheus Test Framework Usage Guide

## Getting Started

### Installation

```bash
pip install -e test-framework/
```

### Basic Structure

A test implementation consists of three main components:

1. Configuration Files
2. Test Steps Definition
3. Test Runner Script

## Creating a Test

### 1. Configuration

#### Test Configuration (config.yaml)

```yaml
# Test Configuration
task_id: "your_task_id" # Task identifier
base_port: 5000 # Base port for worker servers, optional
max_rounds: 3 # Maximum test rounds, optional

# Paths
data_dir: data # Test data directory, optional. defaults to the /data dir within your tests folder
workers_config: workers.json # Worker configuration, relative to tests directory

# MongoDB Configuration (if needed)
mongodb:
  database: your_database_name
  collections:
    collection_name:
      data_file: data.json # Relative to data_dir
      required_count: 1 # Minimum required documents
```

#### Worker Configuration (workers.json)

```json
{
  "worker1": {
    "port": 5001,
    "env": {
      "WORKER_ID": "worker1",
      "OTHER_ENV": "value"
    }
  },
  "worker2": {
    "port": 5002,
    "env": {
      "WORKER_ID": "worker2"
    }
  }
}
```

### 2. Defining Test Steps

Create a `steps.py` file to define your test sequence:

```python
from prometheus_test import TestStep

steps = [
    TestStep(
        name="step_name",                    # Unique step identifier
        description="Step description",       # Human-readable description
        prepare=your_prepare_function,        # Setup function
        execute=your_execute_function,        # Main execution function
        worker="worker_name",                # Worker that executes this step
    ),
    # Add more steps...
]
```

If you need to add extra parameters when calling prepare or execute functions you can `partial` from `functools`

```py
from functools import partial

...
    TestStep(
        name="step_name",
        description="Step description",
        prepare=your_prepare_function,
        execute=partial(your_execute_function, extra_parameter=value),
        worker="worker_name",
    ),
...

```

### 3. Test Runner Script

Create a main test script (e.g., `e2e.py`) that sets up and runs your test sequence:

```python
from pathlib import Path
from prometheus_test import TestRunner
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Import your test steps
from .steps import steps

def main():
    # Create test runner with config from YAML
    base_dir = Path(__file__).parent
    runner = TestRunner(
        steps=steps,
        config_file=base_dir / "config.yaml",
        config_overrides={
            "post_load_callback": your_callback_function  # Optional
        }
    )

    # Run test sequence
    runner.run(force_reset=False)

if __name__ == "__main__":
    main()
```

### 4. Post Load Callback

If you're loading data from JSON files into MongoDB, you may need to do additional post processing (e.g. adding UUIDs). You can define a post load callback in `e2e.py` which will be automatically executed after the MongoDB collections have been populated.

```python
def post_load_callback(db):
    """Modify database after initial load"""
    for doc in db.collection.find():
        # Modify documents as needed
        db.collection.update_one({"_id": doc["_id"]}, {"$set": {"field": "value"}})
```

### 5. ENV Variables

If you have an .env file in your agent's top level folder (for API keys, etc), those environment variables will be automatically loaded into your test script. If you want to add testing specific ENV variables or you need to override any values from you main .env, you can add a second .env in your tests/ directory, which will also be automatically loaded and overrides will be applied.

## Test Data Management

### Directory Structure

```
orca-container
  ├── .env
  ├──src/
  ├──tests/
    ├── .env
    ├── data/
    │    ├── collection1.json
    │    └── collection2.json
    ├── config.yaml
    ├── workers.json
    ├── e2e.py
    └── steps.py
```

### Data Files

Test data should be organized in JSON files within your data directory. Each file represents a collection's initial state. These files are then specified in your config.yaml (see above).

## Writing Test Steps

### Step Functions

Each step requires two main functions:

1. Prepare Function:

```python
def prepare(context):
    """Setup before step execution"""
    # Access configuration
    task_id = context.config.task_id

    # Setup prerequisites
    return {
        "key": "value"  # Data to pass to execute function
    }
```

2. Execute Function:

```python
def execute(context, prepare_data):
    """Execute the test step"""
    # Access data from prepare
    value = prepare_data["key"]

    # Perform test operations, usually a call to the Flask server
    result = some_operation()

    # Sometimes you'll have steps that don't always run, add skip conditions to keep the test running
      result = response.json()
      if response.status_code == 409:
          print("Skipping step")
          return
      elif not result.get("success"):
          raise Exception(
              f"Failed to execute step: {result.get('message')}"
          )
```

## Running Tests

Execute your test script:

```bash
python -m your_package.tests.e2e [--reset]
```

Options:

- `--reset`: Force reset of all databases before running tests

## Resuming a Previous Test

Test state is saved in data_dir/test_state.json. If you run the test without the `--reset` flag, this state file will be used to resume your progress. You can also manually edit the file to alter the point at which you resume, but do note you may have to also edit the local SQLite DB and/or the remote MongoDB instance (if using) in order to keep the state in sync.
