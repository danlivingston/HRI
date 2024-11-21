import json
from time import sleep

from robot.robot_arm_controller import RobotArm

board_positions = None
with open("board_positions.json", "r") as file:
    board_positions = json.load(file)

positions = []
for row in range(1, 9):
    if row % 2 == 1:
        for col in "ABCDEFGH":
            positions.append(f"{col}{row}")
    else:
        for col in "HGFEDCBA":
            positions.append(f"{col}{row}")


def move(board_path: list, mode="l"):
    pos_base = board_positions
    for path in board_path:
        try:
            pos_base = pos_base[path]
        except KeyError:
            print(f"Key Not Found {path}")
            return
    pos_values = pos_base["values"]
    pos_is_pose = pos_base["pose"]
    robot.send_move_command(pos_values, mode=mode, pose=pos_is_pose)


if __name__ == "__main__":
    robot = RobotArm()

    # robot.send_move_command([-0.125, -0.4775, 0.1675, 0, -3.14, 0], mode="j", pose=True)
    # # sleep(3)
    # robot.send_move_command([0.122, -0.2275, 0.17, 0, -3.14, 0], mode="j", pose=True)
    # move(["discard"], "j")
    # move(["discard"], "j")
    # exit()

    print("Move upright")
    move(["upright"], "j")
    sleep(5)

    print("Move init")
    move(["init"], "j")
    sleep(3)

    print("Move hover")
    move(["hover"], "l")
    sleep(2)

    # print("Move discard")
    # move(["discard"], "l")
    # sleep(3)

    # print("Move hover")
    # move(["hover"], "l")
    # sleep(3)

    robot.open_gripper()
    sleep(1)

    print("Move A1 pos")
    move(["A1", "hover"])
    sleep(3)

    # print("Move H8 pos")
    # move(["H8", "hover"])
    # sleep(3)

    # print("Move hover")
    # move(["hover"])
    # sleep(5)

    # print("Move to first hover")
    # move(["A1", "hover"])
    # sleep(3)

    for pos in positions:
        print(f"Move to {pos} hover")
        move([pos, "hover"])
        sleep(0.5)

        print(f"Move to {pos} pickup")
        move([pos, "pickup"])
        sleep(0.5)

        robot.close_gripper()
        sleep(0.5)

        print(f"Move to {pos} hover")
        move([pos, "hover"])
        sleep(0.5)

        # # ! DISCARD

        # move(["discard"])
        # sleep(2)

        # robot.open_gripper()
        # sleep(0.5)

        # # ! /DISCARD

        print(f"Move to {pos} place")
        move([pos, "place"])
        sleep(0.5)

        robot.half_open_gripper()
        sleep(0.5)

        print(f"Move to {pos} hover")
        move([pos, "hover"])
        robot.open_gripper()
        sleep(0.5)
