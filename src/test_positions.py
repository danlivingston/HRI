import json
from time import sleep

from robot.robbot_arm_controller import RobotArm

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


def move(commands):
    for command in commands:
        if isinstance(command, list):
            pos, action = command
            bpos = board_positions[pos][action]
            print(f"Move to {pos} {action}")
            robot.send_move_command(bpos["values"], mode="j", pose=bpos["pose"])
        else:
            print(f"Move to {command}")
            bpos = board_positions[command]
            robot.send_move_command(bpos["values"], mode="j", pose=bpos["pose"])


if __name__ == "__main__":
    robot = RobotArm()
    print("Move upright (j)")
    robot.send_move_command(board_positions["upright"]["values"], mode="j")
    sleep(5)

    print("Move hover (j)")
    robot.send_move_command(board_positions["hover"]["values"], mode="j")
    sleep(5)

    robot.open_gripper()
    sleep(1)

    print("Move A1 pos (j)")
    robot.send_move_command(board_positions[positions[0]]["hover"], mode="j")
    sleep(3)

    print("Move H8 pos (j)")
    robot.send_move_command(board_positions[positions[63]]["hover"], mode="j")
    sleep(3)

    print("Move hover (l)")
    robot.send_move_command(board_positions["hover"], mode="l")
    sleep(5)

    print("Move to first hover (j)")
    robot.send_move_command(board_positions[positions[0]]["hover"], mode="j")
    sleep(3)

    for pos in positions:
        print(f"Move to {pos} hover (j)")
        robot.send_move_command(board_positions[pos]["hover"], mode="j")
        sleep(1)

        print(f"Move to {pos} pickup (l)")
        robot.send_move_command(board_positions[pos]["pickup"], mode="l")
        sleep(1)

        robot.close_gripper()
        sleep(1)

        print(f"Move to {pos} hover (l)")
        robot.send_move_command(board_positions[pos]["hover"], mode="l")
        sleep(1)

        print(f"Move to {pos} place (l)")
        robot.send_move_command(board_positions[pos]["place"], mode="l")
        sleep(1)

        robot.open_gripper()
        sleep(1)

        print(f"Move to {pos} hover (l)")
        robot.send_move_command(board_positions[pos]["hover"], mode="l")
        sleep(1)
