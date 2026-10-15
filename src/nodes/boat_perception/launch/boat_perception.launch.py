from launch import LaunchDescription
from launch_ros.actions import Node

# This file defines how the boat_perception package launches its nodes. Add
# each new node to the launch description below.
# pyright: reportMissingTypeStubs=false
def generate_launch_description():
    return LaunchDescription([
        Node(
            package='boat_perception',
            executable='lidar_processor',
            name='lidar_processor',
            output='screen',
        ),  # type: ignore[arg-type]
    ])
