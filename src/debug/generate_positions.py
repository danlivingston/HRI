import json

piece_hover_height = 0.2
piece_pickup_height = 0.1675
piece_place_height = 0.17
A1_ref = [-0.125, -0.4775, None, 0, -3.14, 0]  # None -> Height
H8_ref = [0.122, -0.2275, None, 0, -3.14, 0]  # None -> Height
center_x = (A1_ref[0] + H8_ref[0]) / 2
center_y = (A1_ref[1] + H8_ref[1]) / 2

ranks = ["1", "2", "3", "4", "5", "6", "7", "8"]
files = ["A", "B", "C", "D", "E", "F", "G", "H"]

board = {
    "upright": {"pose": False, "values": [0, -1.57, 0, 0, 0, 0]},
    "init": {"pose": False, "values": [1.57, -1.57, 1.57, -1.57, -1.57, 0]},
    "hover": {"pose": True, "values": [center_x, center_y, 0.4, 0, -3.14, 0]},
    "discard": {"pose": True, "values": [center_x - 0.3, center_y, 0.2, 0, -3.14, 0]},
    # Emotions
    "watch_board": {"pose": True, "values": [center_x, center_y, 0.4, 2.2, 2.2, 0]},
    "watch_player": {"pose": True, "values": [center_x, center_y, 0.5, 1.2, 1.2, -1.2]},
}

if __name__ == "__main__":

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
                    "hover": {"pose": True, "values": hover},
                    "pickup": {"pose": True, "values": pickup},
                    "place": {"pose": True, "values": place},
                }
        return positions

    board["hover"]["values"][0] = (A1_ref[0] + H8_ref[0]) / 2
    board["hover"]["values"][1] = (A1_ref[1] + H8_ref[1]) / 2
    board["discard"]["values"][0] = (A1_ref[0] + H8_ref[0]) / 2 - 0.3
    board["discard"]["values"][1] = (A1_ref[1] + H8_ref[1]) / 2
    board_positions = generate_board_positions()
    board.update(board_positions)

    with open("board_positions.json", "w") as f:
        json.dump(board, f, indent=4)
