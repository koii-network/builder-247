#!/bin/bash
set -e

# Run tests with coverage
pytest tests/ --cov=prometheus_swarm --cov-report=term-missing --cov-report=xml:coverage.xml

# Optional: Generate HTML coverage report
coverage html