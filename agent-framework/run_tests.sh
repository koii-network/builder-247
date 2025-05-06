#!/bin/bash
set -e

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest

# Optional: Print coverage summary
coverage report