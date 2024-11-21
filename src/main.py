from dotenv import load_dotenv
from loguru import logger

from utils import configure_logger
from robot.controller import RobotController

load_dotenv()

if __name__ == "__main__":
    configure_logger.configure("main")
    logger.info("Starting main")

    robot = RobotController()

    robot.move_piece("A1", "H8")
    robot.discard_piece("H8")

    logger.info("Exiting main")
