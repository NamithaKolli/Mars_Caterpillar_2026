#include <chrono>
#include "behaviortree_cpp/condition_node.h"
#include "rclcpp/rclcpp.hpp"

class TimeRemainingBT : public BT::ConditionNode
{
public:
  TimeRemainingBT(
    const std::string & name,
    const BT::NodeConfiguration & config)
  : BT::ConditionNode(name, config)
  {
    node_ = rclcpp::Node::make_shared("time_remaining_bt");

    start_time_ = node_->now();

    // competition duration in seconds (example: 30 minutes)
    duration_ = rclcpp::Duration::from_seconds(1800.0);
  }

  static BT::PortsList providedPorts()
  {
    return {};
  }

  BT::NodeStatus tick() override
  {
    auto now = node_->now();

    if ((now - start_time_) < duration_) {
      return BT::NodeStatus::SUCCESS;  // keep looping
    } else {
      return BT::NodeStatus::FAILURE;  // stop mission
    }
  }

private:
  rclcpp::Node::SharedPtr node_;
  rclcpp::Time start_time_;
  rclcpp::Duration duration_;
};

#include "behaviortree_cpp/bt_factory.h"

BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<TimeRemainingBT>("TimeRemaining");
}

