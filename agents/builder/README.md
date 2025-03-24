# TESTING

## Testing Individual Workflows

Each agent workflow (see agents/builder/src/workflows) has a `__main__.py` file that can be used to run a test of the individual workflow.

Tests are defined in the `test.py` of each workflow folder, and they inherit from a base WorkflowTest class in `workflows/base.py`.

To run a test:

1. Set your environment variables (see .env.example in agents/builder)

2. Create a virtual environment and install the requirements:

```sh
cd agents/builder

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

3. Run your desired workflow test on the command line:

```sh
python3 -m src.workflows.workflow_name <arguments>
```

There are four arguments set by default on all workflows. These usually do not need to be modified:

- `--client`: defaults to anthropic, can also be openai, xai, or openrouter
- `--model`: each client has a default model set, this can be used to override it
- `--round-number`: defaults to 1
- `--task-id`: defaults to an auto-generated UUID

In addition, each workflow can have its own arguments defined.

### Task Workflow

Creates pull requests based on a description and acceptance criteria.

When this workflow completes, it will print the branch name used. This will be needed when running the merge conflict workflow.

#### Additional arguments

- `--repo`: URL to the target (non-fork) repository (required)
- `--input`: name of CSV file containing task information. Defaults to test_todos.csv. Path can be changed by setting DATA_DIR in .env

#### Required env variables

- `LEADER_GITHUB_TOKEN`, `LEADER_GITHUB_USERNAME`: For creating the fork the pull requests will be made to
- `WORKER1_GITHUB_TOKEN`, `WORKER1_GITHUB_USERNAME`: For making the pull requests
- `DATA_DIR`: path to input file

### Audit Workflow

Reviews a pull request and recommends whether to approve, revise, or reject it.

#### Additional arguments

- `--pr-url`: The URL of a pull request to be reviewed (required)

#### Required env variables

- `WORKER2_GITHUB_TOKEN`, `WORKER2_GITHUB_USERNAME`: For posting a comment with a pull request review.

### Merge Conflict Workflow

Resolves merge conflicts when merging multiple pull requests.

#### Additional arguments

- `--source`: The URL of the fork containing the pull requests to be merged (required)
- `--branch`: The branch the pull requests were made to. Should be in the format task-{task_id}-round-{round_id}, will be printed at the end of the task workflow. (required)

#### Required env variables

- `LEADER_GITHUB_TOKEN`, `LEADER_GITHUB_USERNAME`: For merging the individual todo pull requests and making a consolidated pull request.

## Testing the Task and Audit Flow

1. As with testing individual workflows, set up a virtual environment, install requirements, and set environment variables.

2. Configure and run the middle server locally.

a. Set the task ID to the same value in `agents/builder/.env` and `agents/planner/.env`
b. Add todos to MongoDB. This can be done with a csv file and `agents/planner/src/utils/importTodos.js` Be sure to set REPO_OWNER and REPO_NAME to the target (non-fork) repo's values.
c. Install requirements and run server:

```sh
cd agents/planner
yarn
yarn start
```

3. Run the test script in a separate console

```sh
cd agents/builder
python3 test_endpoints.py
```
