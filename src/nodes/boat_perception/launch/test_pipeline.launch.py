from launch import LaunchDescription
from launch_ros.actions import Node

# TO RUN THE NODE SET, USE THIS COMMAND
# ros2 launch /workspace/src/nodes/boat_perception/boat_perception/launch/test_pipeline.launch.py

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="boat_perception",
            executable="image_feed_node",   # must match your setup.py entry_points
            name="image_feed_node",
            parameters=[{"feed_type": "synthetic", "publish_rate_hz": 10.0}],
        ),
        Node(
            package="boat_perception",
            executable="image_rectifier_node",
            name="image_rectifier_node",
            parameters=[{
                "camera_matrix": [500.0, 0.0, 320.0,
                                  0.0, 500.0, 240.0,
                                  0.0, 0.0, 1.0],
                "distortion_coeffs": [-0.3, 0.1, 0.0, 0.0, 0.0],
                "calib_width": 640,
                "calib_height": 480,
                "alpha": 0.0,
            }],
        ),
        # One viewer for the raw stream, one for the rectified stream
        Node(
            package="boat_perception",
            executable="image_viewer_node",
            name="viewer_raw",
            parameters=[{"topic": "camera/image_raw", "mode": "http", "http_port": 8080}],
        ),
        Node(
            package="boat_perception",
            executable="image_viewer_node",
            name="viewer_rect",
            parameters=[{"topic": "camera/image_rect", "mode": "http", "http_port": 8081}],
        ),
    ])