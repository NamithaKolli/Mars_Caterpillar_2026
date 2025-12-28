cmake_minimum_required(VERSION 3.8)
project(custom_bt_plugins)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -------------------------
# Dependencies
# -------------------------
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav2_behavior_tree REQUIRED)
find_package(behaviortree_cpp REQUIRED)
find_package(pluginlib REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(aruco_msgs REQUIRED)
find_package(action_server_cpp REQUIRED)

# -------------------------
# Build shared library
# -------------------------
add_library(custom_bt_plugins SHARED
  src/start_task_bt_node.cpp
  src/time_remaining.cpp
  src/wait_and_save_aruco_pose.cpp
)

ament_target_dependencies(custom_bt_plugins
  rclcpp
  nav2_behavior_tree
  behaviortree_cpp
  pluginlib
  geometry_msgs
  aruco_msgs
  action_server_cpp
)

# -------------------------
# Export BT plugins
# IMPORTANT: nav2_behavior_tree, not behaviortree_cpp
# -------------------------
pluginlib_export_plugin_description_file(
  nav2_behavior_tree
  plugin.xml
)

# -------------------------
# Install
# -------------------------
install(TARGETS custom_bt_plugins
  LIBRARY DESTINATION lib
)

install(FILES plugin.xml
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
