cmake_minimum_required(VERSION 3.8)
project(boat_startup)

find_package(ament_cmake REQUIRED)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

add_executable(boat_launch src/boat_launch.cpp)
target_include_directories(boat_launch PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>)
target_compile_features(boat_launch PUBLIC c_std_99 cxx_std_17)  # Require C99 and C++17

install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
