import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
...
# parameters are in boat_startup/config/velodyne_drive_node-params.yaml

def generate_launch_description() -> LaunchDescription:
    # Foxglove launch
    foxglove_bridge = ExecuteProcess(cmd=["ros2", "launch", "foxglove_bridge", "foxglove_bridge_launch.xml"])
    startup_share = get_package_share_directory('boat_startup')
    velodyne_params = os.path.join(
        startup_share, 'config', 'velodyne_driver_node-params.yaml'
    )
    return LaunchDescription([
        # velodyne driver node
        Node(
        package='velodyne_driver',
        executable='velodyne_driver_node',
        name='velodyne_driver_node',
        output='screen',
        parameters=[velodyne_params],
        ),
        Node(
        package='velodyne_pointcloud',
        executable='velodyne_transform_node',
        name='velodyne_transform_node',
        output='screen',
        parameters=[velodyne_params],
        ),
        Node(
        package='velodyne_laserscan',
        executable='velodyne_laserscan_node',
        name='velodyne_laserscan_node',
        output='screen',
        parameters=[velodyne_params],
        ),   
        Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_velodyne_tf',
        arguments=[
            '--x', '0.0',
            '--y', '0.0',
            '--z', '0.5',
            '--yaw', '0.0',
            '--pitch', '0.0',
            '--roll', '0.0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'velodyne',
        ],
        ),
        foxglove_bridge
    ])