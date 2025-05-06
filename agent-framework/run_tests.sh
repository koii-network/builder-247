#!/bin/bash
set -e

# Ensure we're in the agent-framework directory
cd "$(dirname "$0")"

# Run tests with coverage
PYTHONPATH=. pytest tests/ --cov=prometheus_swarm --cov-report=term-missing --cov-report=xml:coverage.xml

# Optional: Generate HTML coverage report
coverage html