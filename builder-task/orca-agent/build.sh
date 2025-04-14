#!/bin/bash

# Copy the agent_framework package
cp -r ../../agent-framework/prometheus_swarm .
cp ../../agent-framework/setup.py .

# Build the Docker image
docker build -t labrocadabro/buildertest:0.1 .

# Clean up
rm -rf prometheus_swarm
rm setup.py
