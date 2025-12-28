#include <string>

#include "behaviortree_cpp/condition_node.h"

#include "rclcpp/rclcpp.hpp"

class RemainingTime : public BT::ConditionNode
{
public:
  RemainingTime(
    const std::string & name,
    const BT::NodeConfiguration & config)
  : BT::ConditionNode(name, config),
    duration_(rclcpp::Duration::from_seconds(1800.0))  // ✅ FIX
  {
    node_ = rclcpp::Node::make_shared("remaining_time_bt");
    start_time_ = node_->now();
  }

  static BT::PortsList providedPorts()
  {
    return {};
  }

  BT::NodeStatus tick() override
  {
    if ((node_->now() - start_time_) < duration_) {
      return BT::NodeStatus::SUCCESS;
    }
    return BT::NodeStatus::FAILURE;
  }

private:
  rclcpp::Node::SharedPtr node_;
  rclcpp::Time start_time_;
  rclcpp::Duration duration_;
};

