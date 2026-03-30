#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Define the name and tag for your Docker image
IMAGE_NAME="qc-agent-framework"
TAG="latest"

# --- Build Process ---
echo "▶️ Building Docker image: ${IMAGE_NAME}:${TAG}"

# Run the docker build command from the project root
docker build -t "${IMAGE_NAME}:${TAG}" .

echo "✅ Docker image built successfully!"
echo "   Image: ${IMAGE_NAME}:${TAG}"
echo "   To run it, use: docker run -it --rm ${IMAGE_NAME}:${TAG}"