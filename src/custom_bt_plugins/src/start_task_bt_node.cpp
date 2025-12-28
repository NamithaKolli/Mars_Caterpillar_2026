#include <string>

#include "action_server_cpp/action/manipulator.hpp"
#include "nav2_behavior_tree/bt_action_node.hpp"


class StartTask
  : public nav2_behavior_tree::BtActionNode<action_server_cpp::action::Manipulator>
{
public:
  using Manipulator = action_server_cpp::action::Manipulator;

  StartTask(
  const std::string & xml_tag_name,
  const BT::NodeConfiguration & conf)
: BtActionNode<Manipulator>(xml_tag_name, "manipulator_task", conf)
{}


  static BT::PortsList providedPorts()
  {
    return providedBasicPorts({
      BT::InputPort<int>("arrival_code", "0 = excavation, 2 = drop")
    });
  }

  void on_tick() override
  {
    int arrival_code;
    getInput("arrival_code", arrival_code);
    goal_.arrival_code = static_cast<int8_t>(arrival_code);
  }

  BT::NodeStatus on_success() override
  {
    auto result = result_.result;

    if (result->status_code == 1 || result->status_code == 3) {
      return BT::NodeStatus::SUCCESS;
    }

    return BT::NodeStatus::FAILURE;
  }
};
