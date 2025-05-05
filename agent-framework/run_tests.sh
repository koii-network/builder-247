#!/bin/bash

# Run tests with coverage
pytest tests/ --cov=prometheus_swarm --cov-report=term --cov-report=html

# Display total coverage
coverage report -m