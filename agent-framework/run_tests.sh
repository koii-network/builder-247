#!/bin/bash
set -e

# Activate virtual environment if needed
# source venv/bin/activate  # Uncomment if using a virtual environment

# Install development requirements
pip install -r requirements-dev.txt

# Run tests with coverage
pytest \
    --cov=prometheus_swarm \
    --cov-report=term-missing \
    --cov-report=xml:coverage.xml \
    --cov-report=html:htmlcov