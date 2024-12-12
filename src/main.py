import random
from time import sleep

from dotenv import load_dotenv
from loguru import logger

from robot.controller import RobotController
from robot.emotions import Emotions
from utils import configure_logger

load_dotenv()

if __name__ == "__main__":
    configure_logger.configure("main")
    logger.info("Starting main")

    robot = RobotController()
    # speak demo
    robot.assume_emotion(Emotions.WATCH_PLAYER)
    sleep(3)
    robot.speak(30)

    # move discard demo
    # robot.move_piece("A1", "H8")
    # robot.discard_piece("H8")

    # multi discard demo
    # for row in range(1, 9):
    #     for col in ["A", "B", "C", "D"]:
    #         robot.discard_piece(f"{col}{row}")

    # random place demo
    # current_pos = "B1"
    # for _ in range(10):
    #     place = chr(random.randint(65, 72)) + str(random.randint(1, 8))
    #     robot.move_piece(current_pos, place)
    #     current_pos = place

    logger.info("Exiting main")
