# Summarizer Task Tests

This directory contains end-to-end tests for the summarizer task using the Prometheus test framework.

## Structure

```
tests/
├── config.yaml           # Test configuration
├── workers.json         # Worker configuration
├── data/               # Test data
│   ├── todos.json     # Sample todo items
│   └── issues.json    # Sample issues
├── stages/            # Test stages implementation
├── e2e.py            # Test runner script
└── steps.py          # Test steps definition
```

## Prerequisites

1. Install the test framework:
```bash
pip install -e test-framework/
```

2. Set up environment variables in `.env`:
```
ANTHROPIC_API_KEY=your_test_key
GITHUB_USERNAME=your_test_username
GITHUB_TOKEN=your_test_token
```

## Running Tests

To run the tests:

```bash
python -m tests.e2e
```

To force reset databases before running:

```bash
python -m tests.e2e --reset
```

## Test Flow

1. API Key Validation
   - Validates Anthropic API key

2. GitHub Validation
   - Validates GitHub credentials

3. Todo Management
   - Fetches todos for each worker
   - Generates summaries
   - Submits results

4. Audit Process
   - Workers audit each other's submissions

## Adding New Tests

1. Create a new stage in `stages/`
2. Add stage to `stages/__init__.py`
3. Add test step in `steps.py`
4. Update test data in `data/` if needed
