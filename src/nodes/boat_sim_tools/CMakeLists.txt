cmake_minimum_required(VERSION 3.8)
project(boat_sim_tools)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

add_executable(odom_stand_in src/odom_stand_in.cpp)
ament_target_dependencies(odom_stand_in rclcpp nav_msgs geometry_msgs tf2_ros)
install(TARGETS odom_stand_in DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

ament_package()
