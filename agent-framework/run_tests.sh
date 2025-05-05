#!/bin/bash
set -e

# Install project in editable mode with test extras
pip install -e .[test]

# Run tests with coverage
python -m pytest --cov=prometheus_swarm --cov-report=xml --cov-report=term tests/

# Generate HTML coverage report
coverage html