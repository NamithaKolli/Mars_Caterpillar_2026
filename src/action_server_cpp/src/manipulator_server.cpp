#include <chrono>
#include <memory>
#include <thread>
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "action_server_cpp/action/manipulator.hpp"

using namespace std::chrono_literals;

class ManipulatorActionServer : public rclcpp::Node
{
public:
  using Manipulator = action_server_cpp::action::Manipulator;
  using GoalHandleManipulator = rclcpp_action::ServerGoalHandle<Manipulator>;

  ManipulatorActionServer()
  : Node("manipulator_action_server")
  {
    action_server_ = rclcpp_action::create_server<Manipulator>(
      this,
      "manipulator_action",
      std::bind(&ManipulatorActionServer::handle_goal, this, std::placeholders::_1, std::placeholders::_2),
      std::bind(&ManipulatorActionServer::handle_cancel, this, std::placeholders::_1),
      std::bind(&ManipulatorActionServer::handle_accepted, this, std::placeholders::_1)
    );

    RCLCPP_INFO(this->get_logger(), "Manipulator Action Server started");
  }

private:
  rclcpp_action::Server<Manipulator>::SharedPtr action_server_;

  rclcpp_action::GoalResponse handle_goal(
    const rclcpp_action::GoalUUID &,
    std::shared_ptr<const Manipulator::Goal> goal)
  {
    RCLCPP_INFO(this->get_logger(), "Received task: '%s' with timeout %.2f",
                goal->task_type.c_str(), goal->timeout_sec);
    return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
  }

  rclcpp_action::CancelResponse handle_cancel(
    const std::shared_ptr<GoalHandleManipulator> goal_handle)
  {
    (void)goal_handle;
    RCLCPP_INFO(this->get_logger(), "Received request to cancel goal");
    return rclcpp_action::CancelResponse::ACCEPT;
  }

  void handle_accepted(const std::shared_ptr<GoalHandleManipulator> goal_handle)
  {
    std::thread([this, goal_handle]() {
      execute(goal_handle);
    }).detach();
  }

  void execute(const std::shared_ptr<GoalHandleManipulator> goal_handle)
  {
    auto goal = goal_handle->get_goal();
    auto result = std::make_shared<Manipulator::Result>();

    auto start = std::chrono::steady_clock::now();
    rclcpp::Rate loop_rate(10);

    while (rclcpp::ok()) {
      auto now = std::chrono::steady_clock::now();
      float elapsed = std::chrono::duration<float>(now - start).count();

      if (elapsed > goal->timeout_sec) {
        goal_handle->abort(result);
        result->success = false;
        result->task_type = goal->task_type;
        result->message = "Task timed out";
        RCLCPP_WARN(this->get_logger(), "%s", result->message.c_str());
        return;
      }

      if (elapsed >= std::min(5.0f, goal->timeout_sec)) {
        break;
      }
      loop_rate.sleep();
    }

    goal_handle->succeed(result);
    result->success = true;
    result->task_type = goal->task_type;
    result->message = "Task completed successfully";
    RCLCPP_INFO(this->get_logger(), "%s", result->message.c_str());
  }
};

int main(int argc, char **argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<ManipulatorActionServer>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
