#!/bin/bash
set -e

source /opt/ros/${ROS_DISTRO}/setup.bash

if [ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]; then
  source "/opt/ros/${ROS_DISTRO}/setup.bash"
elif [ -f "/opt/ros/${ROS_DISTRO}/install/setup.bash" ]; then
  source "/opt/ros/${ROS_DISTRO}/install/setup.bash"
fi

if [ -f "/workspace/install/setup.bash" ]; then
  source "/workspace/install/setup.bash"
fi

exec "$@"