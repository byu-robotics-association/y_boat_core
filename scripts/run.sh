#!/usr/bin/env bash

set -euo pipefail

HARDWARE="${1:-linux}"
BRANCH="${2:-main}"
IMAGE="${2:-latest}"

if [ "${HARDWARE}" = "nano" ]; then
    echo "Running for Jetson Nano"
    export DOCKER_IMAGE="${IMAGE:-latest}-nano"
    docker compose pull
    docker compose up -d
    
else
    echo "Running for Linux"
    export DOCKER_IMAGE="${IMAGE:-latest}"
    docker compose pull
    docker compose up -d
fi
