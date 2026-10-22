#!/bin/bash
set -e
if [ -n "$ROS_SOURCE" ] && [ -f "$ROS_SOURCE" ]; then
    source "$ROS_SOURCE"
fi
# Source the workspace overlay if built
if [ -f "/workspace/install/setup.bash" ]; then
    source "/workspace/install/setup.bash"
fi
exec "$@"