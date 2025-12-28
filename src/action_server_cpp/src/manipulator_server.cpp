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
      "manipulator_task",
      std::bind(&ManipulatorActionServer::handle_goal, this, std::placeholders::_1, std::placeholders::_2),
      std::bind(&ManipulatorActionServer::handle_cancel, this, std::placeholders::_1),
      std::bind(&ManipulatorActionServer::handle_accepted, this, std::placeholders::_1)
    );

    RCLCPP_INFO(get_logger(), "Manipulator Action Server started");
  }

private:
  rclcpp_action::Server<Manipulator>::SharedPtr action_server_;

  /* -------- handle goal -------- */
  rclcpp_action::GoalResponse handle_goal(
    const rclcpp_action::GoalUUID &,
    std::shared_ptr<const Manipulator::Goal> goal)
  {
    RCLCPP_INFO(get_logger(), "Received arrival_code: %d", goal->arrival_code);

    if (goal->arrival_code == 0 || goal->arrival_code == 2) {
      return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }

    return rclcpp_action::GoalResponse::REJECT;
  }

  /* -------- handle cancel -------- */
  rclcpp_action::CancelResponse handle_cancel(
    const std::shared_ptr<GoalHandleManipulator>)
  {
    RCLCPP_WARN(get_logger(), "Manipulator task canceled");
    return rclcpp_action::CancelResponse::ACCEPT;
  }

  /* -------- handle accepted -------- */
  void handle_accepted(const std::shared_ptr<GoalHandleManipulator> goal_handle)
  {
    std::thread(
      std::bind(&ManipulatorActionServer::execute, this, std::placeholders::_1),
      goal_handle
    ).detach();
  }

  /* -------- execute task -------- */
  void execute(const std::shared_ptr<GoalHandleManipulator> goal_handle)
  {
    const auto goal = goal_handle->get_goal();
    auto feedback = std::make_shared<Manipulator::Feedback>();
    auto result   = std::make_shared<Manipulator::Result>();

    /* ================= SCOOPING ================= */
    if (goal->arrival_code == 0) {
      RCLCPP_INFO(get_logger(), "Starting SCOOPING task");

      feedback->status_code = 10;  // Scooping (busy)
      goal_handle->publish_feedback(feedback);

      // simulate scooping
      for (int i = 0; i < 5; i++) {
        if (goal_handle->is_canceling()) {
          RCLCPP_WARN(get_logger(), "Scooping canceled");
          goal_handle->canceled(result);
          return;
        }
        rclcpp::sleep_for(1s);
      }

      result->status_code = 1;  // Scooping done
      goal_handle->succeed(result);
      RCLCPP_INFO(get_logger(), "Scooping completed");
      return;
    }

    /* ================= DROPPING ================= */
    if (goal->arrival_code == 2) {
      RCLCPP_INFO(get_logger(), "Starting DROPPING task");

      feedback->status_code = 20;  // Dropping (busy)
      goal_handle->publish_feedback(feedback);

      // simulate dropping
      for (int i = 0; i < 5; i++) {
        if (goal_handle->is_canceling()) {
          RCLCPP_WARN(get_logger(), "Dropping canceled");
          goal_handle->canceled(result);
          return;
        }
        rclcpp::sleep_for(1s);
      }

      result->status_code = 3;  // Dropping done
      goal_handle->succeed(result);
      RCLCPP_INFO(get_logger(), "Dropping completed");
      return;
    }
  }
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ManipulatorActionServer>());
  rclcpp::shutdown();
  return 0;
}
