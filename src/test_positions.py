import json
from time import sleep

from utils.robot_arm import RobotArm

board_positions = None
with open("board_positions.json", "r") as file:
    board_positions = json.load(file)

positions = [
    "A1",
    "B1",
    "C1",
    "D1",
    "E1",
    "F1",
    "G1",
    "H1",
    "A2",
    "B2",
    "C2",
    "D2",
    "E2",
    "F2",
    "G2",
    "H2",
    "A3",
    "B3",
    "C3",
    "D3",
    "E3",
    "F3",
    "G3",
    "H3",
    "A4",
    "B4",
    "C4",
    "D4",
    "E4",
    "F4",
    "G4",
    "H4",
    "A5",
    "B5",
    "C5",
    "D5",
    "E5",
    "F5",
    "G5",
    "H5",
    "A6",
    "B6",
    "C6",
    "D6",
    "E6",
    "F6",
    "G6",
    "H6",
    "A7",
    "B7",
    "C7",
    "D7",
    "E7",
    "F7",
    "G7",
    "H7",
    "A8",
    "B8",
    "C8",
    "D8",
    "E8",
    "F8",
    "G8",
    "H8",
]

if __name__ == "__main__":
    robot = RobotArm()
    print("Move upright (j)")
    robot.send_joint_command(board_positions["upright"], mode="j")
    sleep(5)

    print("Move hover (j)")
    robot.send_joint_command(board_positions["hover"], mode="j")
    sleep(5)

    robot.open_gripper()
    sleep(1)

    print("Move A1 pos (j)")
    robot.send_joint_command(board_positions[positions[0]]["hover"], mode="j")
    sleep(3)

    print("Move H8 pos (j)")
    robot.send_joint_command(board_positions[positions[63]]["hover"], mode="j")
    sleep(3)

    print("Move hover (l)")
    robot.send_joint_command(board_positions["hover"], mode="l")
    sleep(5)

    print("Move to first hover (j)")
    robot.send_joint_command(board_positions[positions[0]]["hover"], mode="j")
    sleep(3)

    for pos in positions:
        print(f"Move to {pos} hover (j)")
        robot.send_joint_command(board_positions[pos]["hover"], mode="j")
        sleep(1)

        print(f"Move to {pos} pickup (l)")
        robot.send_joint_command(board_positions[pos]["pickup"], mode="l")
        sleep(1)

        robot.close_gripper()
        sleep(1)

        print(f"Move to {pos} hover (l)")
        robot.send_joint_command(board_positions[pos]["hover"], mode="l")
        sleep(1)

        print(f"Move to {pos} place (l)")
        robot.send_joint_command(board_positions[pos]["place"], mode="l")
        sleep(1)

        robot.open_gripper()
        sleep(1)

        print(f"Move to {pos} hover (l)")
        robot.send_joint_command(board_positions[pos]["hover"], mode="l")
        sleep(1)
