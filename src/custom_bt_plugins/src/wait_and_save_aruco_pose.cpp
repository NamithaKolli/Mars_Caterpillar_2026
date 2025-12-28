#include <string>
#include <mutex>
#include <memory>

#include "behaviortree_cpp/condition_node.h"
#include "behaviortree_cpp/bt_factory.h"

#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "aruco_msgs/msg/marker_array.hpp"

class WaitAndSaveArucoPose : public BT::ConditionNode
{
public:
  WaitAndSaveArucoPose(
    const std::string& name,
    const BT::NodeConfiguration& config)
  : BT::ConditionNode(name, config)
  {
    node_ = rclcpp::Node::make_shared("wait_and_save_aruco_pose_bt");

    sub_ = node_->create_subscription<aruco_msgs::msg::MarkerArray>(
      "/aruco_markers",
      rclcpp::SensorDataQoS(),
      std::bind(&WaitAndSaveArucoPose::arucoCallback, this, std::placeholders::_1)
    );

    // IMPORTANT:
    // We do NOT spin here.
    // Nav2 / BT engine already spins rclcpp.
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<int>("marker_id"),
      BT::OutputPort<geometry_msgs::msg::PoseStamped>("output_pose")
    };
  }

  BT::NodeStatus tick() override
  {
    std::lock_guard<std::mutex> lock(mutex_);

    // Read marker_id once
    if (marker_id_ < 0) {
      if (!getInput("marker_id", marker_id_)) {
        throw BT::RuntimeError("WaitAndSaveArucoPose: missing marker_id");
      }
    }

    if (pose_received_) {
      setOutput("output_pose", saved_pose_);
      return BT::NodeStatus::SUCCESS;
    }

    return BT::NodeStatus::FAILURE;
  }

private:
  void arucoCallback(const aruco_msgs::msg::MarkerArray::SharedPtr msg)
  {
    std::lock_guard<std::mutex> lock(mutex_);

    if (pose_received_) {
      return;  // 🔒 LATCH: first detection wins
    }

    for (const auto& marker : msg->markers) {
      if (marker.id == marker_id_) {
        saved_pose_.header = msg->header;
        saved_pose_.pose   = marker.pose.pose;
        pose_received_ = true;
        break;
      }
    }
  }

  // ROS
  rclcpp::Node::SharedPtr node_;
  rclcpp::Subscription<aruco_msgs::msg::MarkerArray>::SharedPtr sub_;

  // Data
  geometry_msgs::msg::PoseStamped saved_pose_;
  bool pose_received_{false};
  int marker_id_{-1};

  std::mutex mutex_;
};

BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<WaitAndSaveArucoPose>("WaitAndSaveArucoPose");
}
