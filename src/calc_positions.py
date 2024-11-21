import json
from time import sleep

from utils.robot_arm import RobotArm

board = {
    "upright": [0, -1.57, 0, 0, 0, 0],
    "hover": [1.185327, -0.562231, -0.853332, -0.157442, -1.569887, -0.382749],
    "discard": [],  # TODO
}
piece_hover_height = 0.2
piece_pickup_height = 0.1675
piece_place_height = 0.17
A1_ref = [-0.128, -0.48, None, 0, -3.14, 0]  # None -> Height
H8_ref = [0.125, -0.23, None, 0, -3.14, 0]  # None -> Height

ranks = ["1", "2", "3", "4", "5", "6", "7", "8"]
files = ["A", "B", "C", "D", "E", "F", "G", "H"]


if __name__ == "__main__":
    robot = RobotArm()

    def calc_inverse_kinematic_xy(position):
        inverse = robot.get_inverse_kinematics(position)
        return inverse

    def generate_board_positions():
        positions = {}
        for file in files:
            for rank in ranks:
                coord = f"{file}{rank}"
                x = A1_ref[0] + (H8_ref[0] - A1_ref[0]) * (
                    files.index(file) / (len(files) - 1)
                )
                y = A1_ref[1] + (H8_ref[1] - A1_ref[1]) * (
                    ranks.index(rank) / (len(ranks) - 1)
                )
                hover = [x, y, piece_hover_height, 0, -3.14, 0]
                pickup = [x, y, piece_pickup_height, 0, -3.14, 0]
                place = [x, y, piece_place_height, 0, -3.14, 0]
                positions[coord] = {
                    "hover": calc_inverse_kinematic_xy(hover),
                    "pickup": calc_inverse_kinematic_xy(pickup),
                    "place": calc_inverse_kinematic_xy(place),
                }
                robot.send_joint_command(positions[coord]["hover"])
                sleep(1)
        return positions

    robot.send_joint_command(board["hover"], mode="j")
    sleep(5)
    board_positions = generate_board_positions()
    # board["hover"] = calc_inverse_kinematic_xy(board["hover"])
    board.update(board_positions)
    robot.send_joint_command(board["upright"], mode="j")
    sleep(5)

    with open("board_positions.json", "w") as f:
        json.dump(board, f, indent=4)
