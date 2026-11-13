import math  # Provides sine and cosine for converting heading into a quaternion.
import rclpy  # Provides the ROS 2 Python tools.
from rclpy.node import Node  # Provides the base class for a ROS 2 node.
from rclpy.action import ActionClient  # Provides a client for sending ROS 2 action goals.
from rclpy.utilities import try_shutdown
from nav2_msgs.action import NavigateToPose  # Provides Nav2's "navigate to a pose" action type.
from action_msgs.msg import GoalStatus  # Provides names for action result statuses.
from vision_msgs.msg import Detection3DArray

class Nav2GoalSender(Node):  # Defines a ROS 2 node that can send a goal to Nav2.
    def __init__(self):  # Runs when this node is created.
        super().__init__('Buoy_Pathfinder')  # Gives this node its ROS 2 name.
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')  # Connects to Nav2's goal action.
        self.obstacles = {}  # Stores the latest detected buoy positions.
        self.detection_subscriber = self.create_subscription(  # Creates a listener for the detections topic.
        Detection3DArray,  # Matches the publisher's message type.
        'objects/detections',  # Matches the publisher's topic name.
        self.detections_callback,  # Calls this method whenever a message arrives.
        10  # Sets the message queue size.
        )
        self.goal_sent = False

    def detections_callback(self, msg): # Defines a function to pull data from topic message
        for buoy in msg.detections:
            buoy_id = buoy.id
            x = buoy.bbox.center.position.x
            y = buoy.bbox.center.position.y

            self.obstacles[buoy_id] = (x, y)

        buoy1 = self.obstacles['buoy_1']
        buoy2 = self.obstacles['buoy_2']
        buoy3 = self.obstacles['buoy_3']
        buoy4 = self.obstacles['buoy_4']

        x_goal = (buoy1[0] + buoy2[0]) / 2
        y_goal = (buoy1[1] + buoy2[1]) / 2

        # Set goal angle part of pose as angle to next set of buoys, it is really weird how this works
        # but basically we need to specify
        x_face = (buoy3[0] + buoy4[0])/2
        y_face = (buoy3[1] + buoy4[1])/2
        yaw_goal = math.atan2(y_face - y_goal, x_face - x_goal)

        self.get_logger().info(
            f"Calculated waypoint: ({x_goal}, {y_goal})"
        )

        if not self.goal_sent:
            self.goal_sent = True
            self.send_goal(x_goal, y_goal, yaw_goal)
    
    def send_goal(self, x, y, yaw):  # Defines a function to send a goal position and heading.
        self.get_logger().info('Waiting for Nav2...')  # Prints a message while waiting for Nav2.
        self._client.wait_for_server()  # Waits until Nav2's action server is available.
        goal = NavigateToPose.Goal()  # Creates an empty Nav2 goal.
        goal.pose.header.frame_id = 'map'  # Says the goal coordinates are expressed in the map frame.
        goal.pose.header.stamp = self.get_clock().now().to_msg() # getting time?

        goal.pose.pose.position.x = x  # Sets the goal's x position in meters.
        goal.pose.pose.position.y = y  # Sets the goal's y position in meters.
        goal.pose.pose.position.z = 0.0  # Sets the goal's z position to zero for 2D navigation.
        
        goal.pose.pose.orientation.x = 0.0
        goal.pose.pose.orientation.y = 0.0 # x and y are always zero because we never tilt around those axes
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)  # Converts the requested heading into the quaternion's z part.
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)  # Converts the requested heading into the quaternion's w part.
        self.get_logger().info(f'Sending goal: x={x}, y={y}, yaw={yaw} radians')  # Prints the goal being sent.
        future = self._client.send_goal_async(goal, feedback_callback=self.feedback_callback)  # Sends the goal and requests progress updates.
        future.add_done_callback(self.goal_response_callback)  # Arranges to handle Nav2's response.

    def feedback_callback(self, feedback_message):  # Runs when Nav2 sends a progress update.
        feedback = feedback_message.feedback  # Gets the progress information from the update.
        self.get_logger().info(f'Distance remaining: {feedback.distance_remaining:.2f} m')  # Prints Nav2's estimated remaining distance.

    def goal_response_callback(self, future):  # Runs when Nav2 accepts or rejects the goal.
        goal_handle = future.result()  # Gets Nav2's response to the goal request.
        if not goal_handle.accepted:  # Checks whether Nav2 rejected the goal.
            self.get_logger().error('Nav2 rejected the goal.')  # Prints an error if the goal was rejected.
            return  # Stops handling this rejected goal.
        self.get_logger().info('Nav2 accepted the goal.')  # Prints a message if Nav2 accepted the goal.
        result_future = goal_handle.get_result_async()  # Requests the final result without blocking the node.
        result_future.add_done_callback(self.result_callback)  # Arranges to handle the final result.

    def result_callback(self, future):  # Runs when Nav2 finishes or stops the goal.
        result = future.result()  # Gets Nav2's final result.
        if result.status == GoalStatus.STATUS_SUCCEEDED:  # Checks whether Nav2 reached the goal successfully.
            self.get_logger().info('Nav2 reached the goal.')  # Prints a success message.
        else:  # Handles a goal that did not succeed.
            self.get_logger().error(f'Navigation ended with status {result.status}.')  # Prints the action's result status.

def main(args=None):  # Defines the function that starts and stops this ROS 2 program.
    rclpy.init(args=args)  # Initializes ROS 2 for this program.
    node = Nav2GoalSender()  # Creates this program's ROS 2 node.
    # to be able to uncomment this line, you need to make sure that the Nav2 /navigate_to_pose
    # action is running. Run this command in the container: ros2 launch nav2_bringup navigation_launch.py
    # node.send_goal(x=2.0, y=1.0, yaw=0.0)  # Sends an example goal 2 m east, 1 m north, facing along +x.

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        try_shutdown()

if __name__ == '__main__':  # Checks whether this file was run directly.
    main()  # Starts the ROS 2 node.
