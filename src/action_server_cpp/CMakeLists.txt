cmake_minimum_required(VERSION 3.8)
project(action_server_cpp)

# -------------------------
# Compiler options
# -------------------------
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# -------------------------
# Find dependencies
# -------------------------
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# -------------------------
# Generate action interfaces
# -------------------------
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Manipulator.action"
)

# -------------------------
# Include directories
# -------------------------
include_directories(include)

# -------------------------
# Action server executable
# -------------------------
add_executable(manipulator_action_server
  src/manipulator_server.cpp
)


ament_target_dependencies(manipulator_action_server
  rclcpp
  rclcpp_action
)

# Link generated action interfaces
rosidl_target_interfaces(manipulator_action_server
  ${PROJECT_NAME} "rosidl_typesupport_cpp"
)

# -------------------------
# Install
# -------------------------
install(TARGETS
  manipulator_action_server
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  action
  DESTINATION share/${PROJECT_NAME}
)

# -------------------------
# Export
# -------------------------
ament_export_dependencies(rosidl_default_runtime)

ament_package()
