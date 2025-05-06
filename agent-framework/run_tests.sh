#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
python -m pytest \
    --cov=prometheus_swarm \
    --cov-report=term \
    --cov-report=html:coverage_report \
    tests/