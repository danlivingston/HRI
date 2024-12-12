import asyncio
from time import sleep

from dotenv import load_dotenv
from loguru import logger

from robot.controller import RobotController
from robot.emotions import Emotions
from utils import configure_logger

load_dotenv()


async def main():
    configure_logger.configure("main")
    logger.info("Starting main")

    robot = RobotController()

    # speaking demo
    robot.assume_emotion(Emotions.WATCH_PLAYER)
    sleep(3)
    robot.start_speak()
    await asyncio.sleep(10)
    robot.stop_speak()
    sleep(1)
    robot.assume_emotion(Emotions.WATCH_BOARD)
    sleep(3)

    logger.info("Exiting main")


if __name__ == "__main__":
    asyncio.run(main())
