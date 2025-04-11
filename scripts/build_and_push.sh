#!/bin/bash
set -e

# Configuration
DOCKER_REGISTRY=${DOCKER_REGISTRY:-localhost}
IMAGE_NAME=apollo-appointment-api
TAG=${TAG:-latest}
FULL_IMAGE_NAME=$DOCKER_REGISTRY/$IMAGE_NAME:$TAG

# Build the image
echo "Building Docker image: $FULL_IMAGE_NAME"
docker build -t $FULL_IMAGE_NAME .

# Push to registry
if [ "$DOCKER_REGISTRY" != "localhost" ]; then
    echo "Pushing image to registry: $FULL_IMAGE_NAME"
    docker push $FULL_IMAGE_NAME
    echo "Image pushed successfully"
else
    echo "Skipping push as registry is localhost"
fi

echo "Build and push completed successfully" 