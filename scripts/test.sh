#!/usr/bin/env bash

# Runs the same checks as CI (.github/workflows/ci.yml) locally, so failures
# show up before opening a PR. Keep the two in sync when either changes.

set -euo pipefail

# ruff.toml and the Dockerfile paths are relative to the project root
cd "$(dirname "${BASH_SOURCE[0]}")/.."

RUFF_VERSION=0.16.5
IMAGE=y_boat_core:test
ROS_DISTRO=jazzy
SKIP_RUFF=0
PACKAGES=()

while [ $# -gt 0 ]; do
    case "$1" in
        --no-ruff)
            SKIP_RUFF=1
            shift
            ;;
        -h|--help)
            echo "Usage: $(basename "$0") [--no-ruff] [package ...]"
            echo
            echo "  package    ROS package(s) to test, plus everything that depends on them"
            echo "             (default: test every package)"
            echo "  --no-ruff  skip the type annotation check"
            echo
            echo "Builds the dev image from .docker/dockerfile.dev, builds the whole"
            echo "workspace, then runs the package tests -- the same steps as CI."
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        *)
            PACKAGES+=("$1")
            shift
            ;;
    esac
done

if [ "${SKIP_RUFF}" = 0 ]; then
    if ! command -v ruff > /dev/null; then
        echo "ruff not found. Install it with: pip install ruff==${RUFF_VERSION}" >&2
        echo "(or skip this check with --no-ruff)" >&2
        exit 1
    fi
    if [ "$(ruff --version)" != "ruff ${RUFF_VERSION}" ]; then
        echo "Warning: $(ruff --version) installed, CI uses ${RUFF_VERSION}; results may differ." >&2
    fi
    echo "==> Checking type annotations (ruff)"
    ruff check src .github
fi

echo "==> Building ${IMAGE} from .docker/dockerfile.dev"
docker build -f .docker/dockerfile.dev -t "${IMAGE}" .

TEST_SELECT=""
if [ ${#PACKAGES[@]} -gt 0 ]; then
    TEST_SELECT="--packages-above ${PACKAGES[*]}"
    echo "==> Testing ${PACKAGES[*]} and their dependents"
else
    echo "==> Testing all packages"
fi

# One `docker run` because build/ and install/ live in the container's
# /workspace, outside the bind-mounted src/. ROS is sourced explicitly because
# the image only sources it from /root/.bashrc, which `bash -c` never reads.
docker run --rm \
    -e ROS_DISTRO="${ROS_DISTRO}" \
    -e TEST_SELECT="${TEST_SELECT}" \
    -v "$PWD/src:/workspace/src" \
    "${IMAGE}" \
    bash -c '
        set -e
        source "/opt/ros/$ROS_DISTRO/setup.bash"
        echo "==> Installing package dependencies (rosdep)"
        apt-get update -qq
        rosdep update -q --rosdistro "$ROS_DISTRO"
        rosdep install --from-paths src --ignore-src -y -q --rosdistro "$ROS_DISTRO"

        echo "==> colcon build"
        colcon build

        echo "==> colcon test"
        # colcon test exits 0 even when tests fail; test-result is what
        # prints the failure summary and sets the exit code.
        colcon test $TEST_SELECT
        colcon test-result --verbose
    '
