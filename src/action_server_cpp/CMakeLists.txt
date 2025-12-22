cmake_minimum_required(VERSION 3.5)
project(action_server_cpp)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Generate action messages
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Manipulator.action"
)

# Include directories
include_directories(include)

# Build the action server executable
add_executable(manipulator_server src/manipulator_server.cpp)
ament_target_dependencies(manipulator_server rclcpp rclcpp_action)

# Link generated action
rosidl_target_interfaces(manipulator_server
  ${PROJECT_NAME} "rosidl_typesupport_cpp")

install(TARGETS manipulator_server
  DESTINATION lib/${PROJECT_NAME})

ament_package()
