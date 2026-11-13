from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = Path(get_package_share_directory("boat_image_processing"))
    default_calib = str(share / "config" / "default_camera.yaml")

    return LaunchDescription([
        DeclareLaunchArgument("feed_type", default_value="synthetic"),
        DeclareLaunchArgument("publish_rate_hz", default_value="10.0"),
        DeclareLaunchArgument("camera_info_file", default_value=default_calib),
        DeclareLaunchArgument("alpha", default_value="0.0"),
        DeclareLaunchArgument("foxglove", default_value="true"),
        DeclareLaunchArgument("foxglove_port", default_value="8765"),

        Node(
            package="boat_image_processing",
            executable="image_feed_node",
            name="image_feed_node",
            output="screen",
            parameters=[{
                "feed_type": LaunchConfiguration("feed_type"),
                "publish_rate_hz": LaunchConfiguration("publish_rate_hz"),
                "camera_info_file": LaunchConfiguration("camera_info_file"),
                "image_width": 640,
                "image_height": 480,
            }],
        ),
        Node(
            package="boat_image_processing",
            executable="image_rectifier_node",
            name="image_rectifier_node",
            output="screen",
            parameters=[{"alpha": LaunchConfiguration("alpha")}],
        ),
        # Foxglove WebSocket bridge. Disable with `foxglove:=false`
        Node(
            package="foxglove_bridge",
            executable="foxglove_bridge",
            name="foxglove_bridge",
            output="screen",
            parameters=[{
                "port": ParameterValue(LaunchConfiguration("foxglove_port"), value_type=int),
            }],
            condition=IfCondition(LaunchConfiguration("foxglove")),
        ),
    ])