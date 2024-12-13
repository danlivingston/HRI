import asyncio
import json
from time import sleep  # TODO: replace with asyncio.sleep()?

from loguru import logger

from robot.emotions import Emotions
from robot.robot_arm_controller import RobotArm

with open("board_positions.json", "r") as file:
    BOARD_POSITIONS = json.load(file)


class RobotController:
    speak = False

    def __init__(self):
        logger.info("Initializing RobotController")
        self.robot = RobotArm()

        logger.debug("Moving upright")
        self.assume_emotion(Emotions.UPRIGHT, mode="j")
        sleep(4)

        logger.debug("Moving init")
        self.assume_emotion(Emotions.INIT, mode="j")
        self.robot.open_gripper()
        sleep(3.1)

        logger.debug("Moving watch player")
        self.assume_emotion(Emotions.WATCH_PLAYER)
        sleep(3.1)
        logger.info("RobotController ready")

    def move(self, board_path: list, mode="l", time=2):
        pos_base = BOARD_POSITIONS
        for path in board_path:
            try:
                pos_base = pos_base[path]
            except KeyError:
                print(f"Key Not Found {path}")
                return
        pos_values = pos_base["values"]
        pos_is_pose = pos_base["pose"]
        self.robot.send_move_command(pos_values, mode=mode, pose=pos_is_pose, t=time)

    def assume_emotion(self, emotion: Emotions, mode="l"):
        if not isinstance(emotion, Emotions):
            raise ValueError("Invalid emotion")

        logger.info(f"Robot is assuming the emotion: {emotion.value}")
        self.move([emotion.value], mode)

    async def speaking_task(self):
        logger.info("Starting speak")
        while True:
            self.robot.send_gripper_command(180)
            await asyncio.sleep(0.25)
            # sleep(0.25)
            self.robot.send_gripper_command(255)
            # sleep(0.25)
            await asyncio.sleep(0.25)

    def start_speak(self):
        self.speak_task = asyncio.create_task(self.speaking_task())

    def stop_speak(self):
        logger.info("Stopping speak")
        if self.speak_task:
            self.speak_task.cancel()
            self.speak_task = None

    def speak_for_duration(self, duration):
        self.start_speak()
        sleep(duration)
        self.stop_speak()

    def move_piece(self, pos_A, pos_B):
        logger.info(f"Moving {pos_A} to {pos_B}")
        # Verify key exists, A1-H8
        if pos_A not in BOARD_POSITIONS or pos_B not in BOARD_POSITIONS:
            logger.error(f"Invalid position: {pos_A} or {pos_B}")
            return

        self.move([pos_A, "hover"], time=2)
        sleep(2.1)
        self.move([pos_A, "pickup"], time=1)
        sleep(1.1)
        self.robot.close_gripper()
        sleep(0.5)
        self.move([pos_A, "hover"], time=1)
        sleep(1.1)
        self.move([pos_B, "hover"], time=2)
        sleep(2.1)
        self.move([pos_B, "place"], time=1)
        sleep(1.1)
        self.robot.half_open_gripper()
        sleep(0.5)
        self.move([pos_B, "hover"], time=1)
        self.robot.open_gripper()
        sleep(1.1)
        # self.move(["hover"], time=2)
        self.assume_emotion(Emotions.WATCH_PLAYER)
        sleep(2.1)

    # ! Pieces start to stack an overflow eventually, TODO: multiple discard positions?
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

        self.assume_emotion(Emotions.DISCARD)
        sleep(2)
        self.robot.half_open_gripper()
        sleep(0.5)

        self.assume_emotion(Emotions.HOVER)
        self.robot.open_gripper()
        sleep(2)
