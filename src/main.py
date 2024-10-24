from dotenv import load_dotenv
from loguru import logger

from helloworld import say_hello
from utils import configure_logger

from utils.robot_arm import RobotArm

from time import sleep

# pickup_height = 0.1675
# hover_height = 0.18

zero_point = [0.125, -0.23, 0.1675, 0, -3.14, 0]
# zero_point = [0, -0.23, 0.1675, 0, -3.14, 0]
zero_point_h = [0.125, -0.23, 0.2, 0, -3.14, 0]
transition_point = [0, -0.35, 0.4, 0, -3.14, 0]  # center


one_point = [-0.128, -0.48, 0.1675, 0, -3.14, 0]
one_point_p = [-0.128, -0.48, 0.18, 0, -3.14, 0]
one_point_h = [-0.128, -0.48, 0.2, 0, -3.14, 0]

load_dotenv()

if __name__ == "__main__":
    configure_logger.configure("main")
    logger.debug("starting main")
    say_hello()

    ###################################3

    robot = RobotArm()
    sleep(1)

    robot.open_gripper()
    sleep(1)

    inverse = robot.get_inverse_kinematics(zero_point_h)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(zero_point)
    robot.send_joint_command(inverse)
    sleep(1)

    robot.close_gripper()
    sleep(1)

    inverse = robot.get_inverse_kinematics(zero_point_h)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(transition_point)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(one_point_h)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(one_point_p)
    robot.send_joint_command(inverse)
    sleep(1)

    robot.open_gripper()
    sleep(1)

    inverse = robot.get_inverse_kinematics(transition_point)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(one_point_h)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(one_point)
    robot.send_joint_command(inverse)
    sleep(1)

    robot.close_gripper()
    sleep(1)

    inverse = robot.get_inverse_kinematics(one_point_h)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(transition_point)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(zero_point_h)
    robot.send_joint_command(inverse)
    sleep(1)

    inverse = robot.get_inverse_kinematics(zero_point)
    robot.send_joint_command(inverse)
    sleep(1)

    robot.open_gripper()
    sleep(1)

    inverse = robot.get_inverse_kinematics(transition_point)
    robot.send_joint_command(inverse)
    sleep(1)

    # robot.start_pos()
    # robot.send_gripper_command(0)
    # sleep(3)

    # §§§§§§§§
    # robot.open_gripper()
    # sleep(1)
    # # inverse = robot.get_inverse_kinematics([0.125, -0.23, 0.1675, 0, -3.14, 0])
    # # robot.send_joint_command(inverse)
    # # # sleep(1)
    # # # inverse = robot.get_inverse_kinematics([0.05, -0.23, 0.1675, 0, -3.14, 0])
    # # # robot.send_joint_command(inverse)
    # # sleep(1)
    # inverse = robot.get_inverse_kinematics([-0.128, -0.48, 0.1675, 0, -3.14, 0])
    # robot.send_joint_command(inverse)
    # sleep(1)

    robot.close_connection()

    ######################################3

    logger.debug("exiting main")
