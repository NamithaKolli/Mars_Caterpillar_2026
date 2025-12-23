cmake_minimum_required(VERSION 3.8)
project(custom_bt_plugins)
cmake_minimum_required(VERSION 3.8)
project(custom_bt_plugins)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(nav2_behavior_tree REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)
find_package(action_server_cpp REQUIRED)

include_directories(include)

add_library(custom_bt_plugins SHARED
  src/start_task_bt_node.cpp
  src/time_remaining_bt_node.cpp
)
pluginlib_export_plugin_description_file(
  nav2_behavior_tree
  plugin/plugin.xml
)

ament_target_dependencies(custom_bt_plugins
  rclcpp
  nav2_behavior_tree
  behaviortree_cpp_v3
  action_server_cpp
)

target_compile_definitions(custom_bt_plugins
  PRIVATE BT_PLUGIN_EXPORT
)

install(
  TARGETS custom_bt_plugins
  LIBRARY DESTINATION lib
)

install(
  DIRECTORY plugin
  DESTINATION share/${PROJECT_NAME}
)

ament_package()


