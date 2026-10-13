from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    enable = LaunchConfiguration('enable')
    return LaunchDescription([
        DeclareLaunchArgument(
            'enable', default_value='true',
            description='Set false once perception publishes odometry and TF'),
        Node(
            package='boat_sim_tools',
            executable='odom_stand_in',
            name='odom_stand_in',
            output='screen',
            parameters=[{'use_sim_time': True}],
            condition=IfCondition(enable),
        ),
    ])
