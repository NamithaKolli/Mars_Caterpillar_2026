#include <string>

#include "nav2_behavior_tree/bt_action_node.hpp"
#include "action_server_cpp/action/manipulator.hpp"

using ManipulatorAction = action_server_cpp::action::Manipulator;

class StartTaskBT
  : public nav2_behavior_tree::BtActionNode<ManipulatorAction>
{
public:
  StartTaskBT(
    const std::string & xml_tag_name,
    const BT::NodeConfiguration & conf)
  : BtActionNode<ManipulatorAction>(xml_tag_name, conf, "manipulator_server")
  {}

  static BT::PortsList providedPorts()
  {
    return providedBasicPorts({
      BT::InputPort<std::string>("task_type")
    });
  }

  void on_tick() override
  {
    std::string task;
    getInput("task_type", task);
    goal_.task_type = task;
  }
};

#include "behaviortree_cpp/bt_factory.h"

BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<StartTaskBT>("StartTask");
}

