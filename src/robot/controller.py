from emotions import Emotions
from loguru import logger


class RobotController:
    def __init__(self):
        self.robot = None  # TODO

    def assume_emotion(self, emotion: Emotions):
        if not isinstance(emotion, Emotions):
            raise ValueError("Invalid emotion")
        logger.debug(f"Robot is assuming the emotion: {emotion.value}")
        # TODO

    def move_piece(self, pos_A, pos_B):
        # TODO: Verify key exists, A1-H8
        pass

    def discard_piece(self, from_pos):
        # TODO
        pass
