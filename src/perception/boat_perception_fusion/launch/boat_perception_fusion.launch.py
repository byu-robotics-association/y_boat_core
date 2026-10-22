from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushROSNamespace


def generate_launch_description() -> LaunchDescription:
    launch_description = LaunchDescription()
    object_association_node = Node(
        package='boat_perception_fusion',
        executable='object_association_node',
        name='object_association',
        output='screen',
    )

    node_group = GroupAction([PushROSNamespace('perception'), object_association_node])

    launch_description.add_action(node_group)
    return launch_description
