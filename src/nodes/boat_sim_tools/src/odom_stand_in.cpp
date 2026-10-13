#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"

#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2_ros/transform_broadcaster.h"
#include "tf2_ros/static_transform_broadcaster.h"



using Odometry = nav_msgs::msg::Odometry;

class OdomStandIn : public rclcpp::Node {
    public:
        OdomStandIn() : Node("odom_stand_in") {
            RCLCPP_INFO(get_logger(), "odom_stand_in started");
            std::string input_topic =
        declare_parameter<std::string>("input_topic", "/sim/ground_truth/odom");

        sub_ = create_subscription<Odometry>(
            input_topic, 10,
            [this](const Odometry::SharedPtr msg) { on_odom(msg); });
        pub_ = create_publisher<Odometry>("/odometry/filtered", 10);
        tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
        static_broadcaster_ = std::make_unique<tf2_ros::StaticTransformBroadcaster>(*this);

        geometry_msgs::msg::TransformStamped map_to_odom;
        map_to_odom.header.stamp = now();
        map_to_odom.header.frame_id = "map";
        map_to_odom.child_frame_id = "odom";
        map_to_odom.transform.rotation.w = 1.0;
        static_broadcaster_->sendTransform(map_to_odom);



        RCLCPP_INFO(get_logger(), "listening on %s", input_topic.c_str());
        }
    private:
        rclcpp::Subscription<Odometry>::SharedPtr sub_;
        rclcpp::Publisher<Odometry>::SharedPtr pub_;
        std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
        std::unique_ptr<tf2_ros::StaticTransformBroadcaster> static_broadcaster_;




        void on_odom(const Odometry::SharedPtr msg)
        {
            pub_->publish(*msg);
            RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 1000,
                                "x=%.2f y=%.2f", msg->pose.pose.position.x,
                                msg->pose.pose.position.y);
            geometry_msgs::msg::TransformStamped t;
            t.header.stamp = msg->header.stamp;
            t.header.frame_id = msg->header.frame_id;
            t.child_frame_id = msg->child_frame_id;
            t.transform.translation.x = msg->pose.pose.position.x;
            t.transform.translation.y = msg->pose.pose.position.y;
            t.transform.translation.z = msg->pose.pose.position.z;
            t.transform.rotation = msg->pose.pose.orientation;
            tf_broadcaster_->sendTransform(t);


        }

};

int main (int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<OdomStandIn>());
  rclcpp::shutdown();
  return 0;
}