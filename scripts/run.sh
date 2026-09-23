#!/usr/bin/env bash

set -euo pipefail

# compose reads docker-compose.yml and .env from the project root
cd "$(dirname "${BASH_SOURCE[0]}")/.."

INTERACTIVE=0
PULL_IMAGE=0

while [ $# -gt 0 ]; do
    case "$1" in
        -p|--pull)
            PULL_IMAGE=1
            shift
            ;;
        -i|--interactive)
            INTERACTIVE=1
            shift
            ;;
        -h|--help)
            echo "Usage: $(basename "$0") [-i] [-p]"
            echo
            echo "  -i   open an interactive shell once the container is up"
            echo "  -p   pulls the docker image from docker.io"
            echo
            echo "Image tag and ROS distro come from .env (DOCKER_IMAGE, ROS_DISTRO)."
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [ ! -f .env ]; then
    echo "No .env found. Copy .env-example to .env and set DOCKER_IMAGE / ROS_DISTRO." >&2
    exit 1
fi

source .env

: "${DOCKER_IMAGE:?not set in .env}"
: "${ROS_DISTRO:?not set in .env}"

echo "Running yrobotics/y_boat_core:${DOCKER_IMAGE} (ROS_DISTRO=${ROS_DISTRO})"

if [ "${PULL_IMAGE}" = 1 ]; then
    docker compose pull
fi

if [ "${INTERACTIVE}" = 1 ]; then
    docker compose up -d
    exec docker compose exec dev /entrypoint.sh bash
else
    docker compose up
fi
