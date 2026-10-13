from launch import LaunchDescription
from launch_ros.actions import Node


# This file defines how the boat_image_processing package launches its nodes. Add
# each new node to the launch description below.
# pyright: reportMissingTypeStubs=false
def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        Node(
            package='boat_image_processing',
            executable='object_detector',
            name='object_detector',
            output='screen',
        ),  # type: ignore[arg-type]
    ])
