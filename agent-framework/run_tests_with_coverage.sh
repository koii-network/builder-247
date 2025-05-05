#!/bin/bash
# Run tests with coverage reporting

# Ensure script is executable
chmod +x run_tests_with_coverage.sh

# Run tests with pytest and coverage
pytest --cov=prometheus_swarm --cov-report=html --cov-report=term-missing tests/

# Open HTML coverage report (optional, can be commented out)
# xdg-open coverage_html_report/index.html