from robot.emotions import Emotions
from loguru import logger
from time import sleep

import json
from robot.robot_arm_controller import RobotArm

with open("board_positions.json", "r") as file:
    BOARD_POSITIONS = json.load(file)


class RobotController:
    def __init__(self):
        logger.info("Initializing RobotController")
        self.robot = RobotArm()
        logger.debug("Moving upright")
        self.move(["upright"], mode="j")
        sleep(5)
        logger.debug("Moving init")
        self.move(["init"], mode="j")
        self.robot.open_gripper()
        sleep(3)
        logger.debug("Moving hover")
        self.move(["hover"])
        sleep(2)
        logger.info("RobotController ready")

    def move(self, board_path: list, mode="l"):
        pos_base = BOARD_POSITIONS
        for path in board_path:
            try:
                pos_base = pos_base[path]
            except KeyError:
                print(f"Key Not Found {path}")
                return
        pos_values = pos_base["values"]
        pos_is_pose = pos_base["pose"]
        self.robot.send_move_command(pos_values, mode=mode, pose=pos_is_pose)

    def assume_emotion(self, emotion: Emotions):
        if not isinstance(emotion, Emotions):
            raise ValueError("Invalid emotion")
        logger.debug(f"Robot is assuming the emotion: {emotion.value}")
        # TODO

    def move_piece(self, pos_A, pos_B):
        logger.info(f"Moving {pos_A} to {pos_B}")
        # TODO: Verify key exists, A1-H8
        self.move([pos_A, "hover"])
        sleep(2)
        self.move([pos_A, "pickup"])
        sleep(0.5)
        self.robot.close_gripper()
        sleep(0.5)
        self.move([pos_A, "hover"])
        sleep(0.5)
        self.move([pos_B, "hover"])
        sleep(2)
        self.move([pos_B, "place"])
        sleep(0.5)
        self.robot.half_open_gripper()
        sleep(0.5)
        self.move([pos_B, "hover"])
        self.robot.open_gripper()
        sleep(0.5)
        self.move(["hover"])
        sleep(2)

    def discard_piece(self, from_pos):
        logger.info(f"Discarding {from_pos}")
        self.move([from_pos, "hover"])
        sleep(2)
        self.move([from_pos, "pickup"])
        sleep(0.5)
        self.robot.close_gripper()
        sleep(0.5)
        self.move([from_pos, "hover"])
        sleep(0.5)
        self.move(["discard"])
        sleep(2)
        self.robot.half_open_gripper()
        sleep(0.5)
        self.move(["hover"])
        self.robot.open_gripper()
        sleep(2)
