#include <atomic>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/int16.hpp"

#include "behaviortree_cpp/action_node.h"


using namespace std::chrono_literals;

class StartHardcodedExcavateDump : public BT::StatefulActionNode
{
public:
  StartHardcodedExcavateDump(
    const std::string & name,
    const BT::NodeConfiguration & config)
  : BT::StatefulActionNode(name, config),
    done_(false),
    sent_start_(false)
  {
    node_ = rclcpp::Node::make_shared("start_hardcoded_excavate_dump_bt");

    start_pub_ = node_->create_publisher<std_msgs::msg::Int16>(
      "/start_hardcoded_excavate_dump", 10);

    done_sub_ = node_->create_subscription<std_msgs::msg::Int16>(
      "/hardcoded_excavate_dump_done",
      10,
      std::bind(&StartHardcodedExcavateDump::doneCallback, this, std::placeholders::_1)
    );
  }

  // BT ports (optional, you already pass pose via Python)
  static BT::PortsList providedPorts()
  {
    return {};
  }

  // ─────────────────────────────────────────────
  BT::NodeStatus onStart() override
  {
    RCLCPP_INFO(node_->get_logger(), "[BT] StartHardcodedExcavateDump: START");

    done_ = false;
    sent_start_ = false;

    return BT::NodeStatus::RUNNING;
  }

  // ─────────────────────────────────────────────
  BT::NodeStatus onRunning() override
  {
    if (!sent_start_) {
      std_msgs::msg::Int16 msg;
      msg.data = 1;
      start_pub_->publish(msg);

      RCLCPP_INFO(node_->get_logger(), "[BT] Sent START command");
      sent_start_ = true;
    }

    if (done_) {
      RCLCPP_INFO(node_->get_logger(), "[BT] Mission DONE → SUCCESS");
      return BT::NodeStatus::SUCCESS;
    }

    return BT::NodeStatus::RUNNING;
  }

  // ─────────────────────────────────────────────
  void onHalted() override
  {
    RCLCPP_WARN(node_->get_logger(), "[BT] StartHardcodedExcavateDump HALTED");
    done_ = false;
    sent_start_ = false;
  }

private:
  void doneCallback(const std_msgs::msg::Int16::SharedPtr msg)
  {
    if (msg->data == 1) {
      done_ = true;
    }
  }

  rclcpp::Node::SharedPtr node_;

  rclcpp::Publisher<std_msgs::msg::Int16>::SharedPtr start_pub_;
  rclcpp::Subscription<std_msgs::msg::Int16>::SharedPtr done_sub_;

  std::atomic<bool> done_;
  bool sent_start_;
};

#include "behaviortree_cpp/bt_factory.h"

BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<StartHardcodedExcavateDump>("StartHardcodedExcavateDump");
}
