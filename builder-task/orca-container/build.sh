#!/bin/bash

# Copy the agent_framework package
cp -r ../../agent-framwork/agent_framework .
cp ../../agent-framwork/setup.py .

# Build the Docker image
docker build -t labrocadabro/buildertest:0.1 .

# Clean up
rm -rf agent_framework
rm setup.py
