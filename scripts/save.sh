#!/usr/bin/env bash

set -euo pipefail

BRANCH="${1:-main}"
IMAGE_TAG="${1:-latest}"
# REPO_DIR="/path/to/repo"

if [ -z "${1:-}"]; then
    echo "Pushing to main"
    docker build -t yrobotics/y_boat_core:latest -f ./.docker/dockerfile.dev .
    docker push yrobotics/y_boat_core:latest

    docker build -t yrobotics/y_boat_core:latest-nano -f ./.docker/dockerfile.nano .
    docker push yrobotics/y_boat_core:latest-nano
fi 
# else
#     echo "Pushing Branch" 
#     docker build -t yrobotics/y_boat_core:${IMAGE_TAG} -f ../.docker/../
#     docker push yrobotics/y_boat_core:${IMAGE_TAG}
# fi

