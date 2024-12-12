import os
import cv2
import logging
import time
import threading
from typing import Optional, Dict, Any, Tuple, List

import yaml

from chess_logic.chess_cube_processor import ChessCubeProcessor
from computer_vision.compare_move import compare_cube_positions_new_and_missing


class ChessCubeAnalyzer(threading.Thread):
    def __init__(
        self, config_path: str = None, debug: bool = False, camera_index: int = 1
    ):
        super().__init__()
        self.daemon = True  # Allows thread to be killed when main thread exits

        self.debug = debug
        self.logger = logging.getLogger(self.__class__.__name__)

        # Determine the path to the configuration file
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "resources", "config", "settings.yaml"
            )
        else:
            if not os.path.isabs(config_path):
                config_path = os.path.join(os.path.dirname(__file__), config_path)

        config_path = os.path.abspath(config_path)
        self.logger.debug(f"Using config path: {config_path}")  # For debugging purposes

        # Load configuration
        self.config = self.load_config(config_path)

        # Define quadrilateral points from config
        self.chessboard_points = [
            tuple(point) for point in self.config.get("chessboard_points", [])
        ]
        self.obstacle_detection_points = [
            tuple(point) for point in self.config.get("obstacle_detection_points", [])
        ]

        # Initialize ChessCubeProcessor
        self.processor = ChessCubeProcessor(
            config_path=config_path,
            debug=debug,
            chessboard_points=self.chessboard_points,
            obstacle_detection_points=self.obstacle_detection_points,
        )

        # Initialize webcam
        self.camera_index = self.config.get("camera_id", camera_index)
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.get("camera_width", 1920))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.get("camera_height", 1080))

        if not self.cap.isOpened():
            self.logger.error(
                f"Error: Could not open webcam with index {self.camera_index}."
            )
            raise IOError(f"Cannot open webcam with index {self.camera_index}.")

        self.logger.info("Webcam opened successfully.")

        # Initialize camera (warm-up for 5 seconds)
        self.initialize_camera()

        # Initialize obstacle detection
        ret, frame = self.cap.read()
        if not ret:
            self.logger.error("Error: Failed to capture initial image from webcam.")
            raise IOError("Cannot capture initial image from webcam.")
        self.processor.initialize_obstacle_detection(frame)

        # Initialize positions
        self.initial_positions: Dict[str, str] = {}
        self.updated_positions: Dict[str, str] = {}

        # Lock for thread-safe position updates
        self.lock = threading.Lock()

        # Event to signal thread to stop
        self.stop_event = threading.Event()

        # Initialize obstacle flag
        self.obstacle_present = False  # <--- Added flag

        # Start the obstacle detection thread
        self.obstacle_thread = threading.Thread(
            target=self.run_obstacle_detection, daemon=True
        )
        self.obstacle_thread.start()

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        logging.getLogger("ChessCubeAnalyzer").debug(
            f"Configuration loaded from {config_path}."
        )
        return config

    def initialize_camera(self):
        """
        Warm up the camera for 5 seconds to allow auto-exposure, white balance, and other settings to stabilize.
        """
        self.logger.info("Initializing camera. Waiting for 5 seconds...")
        start_time = time.time()

        while time.time() - start_time < 5:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.warning(
                    "Failed to read frame during camera initialization."
                )
                continue

            # Optionally, show the frame to observe progress (can be disabled)
            if self.processor.debug:
                cv2.imshow("Initializing Camera", frame)
                if cv2.waitKey(1) & 0xFF == ord(
                    "q"
                ):  # Allow exiting during initialization
                    self.logger.info("Exiting camera initialization.")
                    break

        cv2.destroyAllWindows()  # Close the initialization window
        self.logger.info("Camera initialization completed.")

    def run_obstacle_detection(self):
        self.logger.info("Starting obstacle detection thread.")
        try:
            while not self.stop_event.is_set():
                start_time = time.time()

                ret, frame = self.cap.read()
                if not ret:
                    self.logger.error("Error: Failed to capture image from webcam.")
                    continue

                # Check for obstacle
                obstacle_present = self.processor.detect_obstacle(frame)
                with self.lock:
                    self.obstacle_present = obstacle_present  # <--- Update the flag

                if obstacle_present:
                    self.logger.warning("Obstacle detected.")
                else:
                    self.logger.info("No obstacle detected.")

                # Calculate elapsed time and sleep for the remaining time to make it 1 second
                elapsed_time = time.time() - start_time
                sleep_time = max(0, 1.0 - elapsed_time)
                time.sleep(sleep_time)

        except Exception as e:
            self.logger.error(f"Exception in obstacle detection thread: {e}")

    def initial(self) -> Optional[str]:
        """
        Capture and store the initial cube positions.
        """
        with self.lock:
            if self.obstacle_present:  # <--- Check obstacle flag
                self.logger.warning(
                    "Cannot perform initial capture: Obstacle detected."
                )
                return "obstacle detected"

        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.error(
                    "Error: Failed to capture image from webcam during initial capture."
                )
                return None

            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image_name = f"initial_frame_{timestamp}.jpg"

            obstacle_detected, initial_positions = self.processor.process_image(
                frame, image_name
            )
            if obstacle_detected:
                self.logger.warning("Obstacle detected during initial capture.")
                return "obstacle detected"

            if initial_positions is None:
                self.logger.info(
                    f"No cubes detected in {image_name} during initial capture."
                )
                return "No cubes detected during initial capture."

            self.initial_positions = initial_positions
            self.logger.info("Initial cube positions captured and stored.")

            return "initial capture completed"

    def update(self) -> Optional[str]:
        """
        Capture and store the updated cube positions.
        """
        with self.lock:
            if self.obstacle_present:  # <--- Check obstacle flag
                self.logger.warning("Cannot perform update capture: Obstacle detected.")
                return "obstacle detected"

        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.error(
                    "Error: Failed to capture image from webcam during update."
                )
                return None

            timestamp = time.strftime("%Y%m%d-%H%M%S")
            image_name = f"update_frame_{timestamp}.jpg"

            obstacle_detected, updated_positions = self.processor.process_image(
                frame, image_name
            )
            if obstacle_detected:
                self.logger.warning("Obstacle detected during update capture.")
                return "obstacle detected"

            if updated_positions is None:
                self.logger.info(
                    f"No cubes detected in {image_name} during update capture."
                )
                return "No cubes detected during update capture."

            self.updated_positions = updated_positions
            self.logger.info("Updated cube positions captured and stored.")

            return "update capture completed"

    def compareMove(self) -> Optional[str]:
        """
        Compare initial and updated cube positions to detect movements.
        Returns the movement string(s) or appropriate message.
        """
        with self.lock:
            if self.obstacle_present:  # <--- Check obstacle flag
                self.logger.warning("Cannot compare moves: Obstacle detected.")
                return "obstacle detected"

            if not self.initial_positions:
                self.logger.warning(
                    "Initial positions not set. Please run 'initial()' first."
                )
                return "initial positions not set"

            if not self.updated_positions:
                self.logger.warning(
                    "Updated positions not set. Please run 'update()' first."
                )
                return "updated positions not set"

            movements = compare_cube_positions_new_and_missing(
                self.initial_positions, self.updated_positions
            )

            movement_strings = []
            movement_targets = (
                set()
            )  # To track movement targets and prevent redundant removals

            for from_position, to_position in movements:
                if from_position and to_position:
                    if from_position != to_position:
                        # Movement from one position to another
                        movement_description = (
                            f"Cube moved from {from_position} to {to_position}"
                        )
                        movement_string = (
                            f"{from_position.lower()}{to_position.lower()}"
                        )
                        movement_strings.append(movement_string)
                        movement_targets.add(to_position)
                    else:
                        # Capture or replacement at the same position
                        movement_description = (
                            f"Cube at {from_position} was captured and replaced"
                        )
                        movement_string = f"{from_position.lower()}captured"
                        movement_strings.append(movement_string)
                elif from_position:
                    # Cube was removed
                    # Check if the removal position is a movement target to prevent redundancy
                    if from_position not in movement_targets:
                        movement_description = f"Cube at {from_position} was removed."
                        movement_string = f"{from_position.lower()}removed"
                        movement_strings.append(movement_string)
                elif to_position:
                    # New cube detected
                    movement_description = f"New cube detected at {to_position}."
                    movement_string = f"new{to_position.lower()}"
                    movement_strings.append(movement_string)

                print(movement_description)

            # Reset initial_positions to updated_positions for future comparisons
            self.initial_positions = self.updated_positions.copy()
            self.updated_positions = {}

            self.logger.info("Cube positions updated after comparison.")

            # Return only valid movement strings (excluding removals if they are movement targets)
            return (
                ", ".join(movement_strings)
                if movement_strings
                else "No movement detected."
            )

    def run(self):
        """
        The main loop of the analyzer thread.
        Currently, obstacle detection runs in its own thread started in __init__.
        This run method can be used for other continuous tasks if needed.
        """
        self.logger.info("ChessCubeAnalyzer main thread started.")
        try:
            while not self.stop_event.is_set():
                # You can implement other continuous tasks here if necessary
                time.sleep(0.1)  # Sleep briefly to reduce CPU usage
        except Exception as e:
            self.logger.error(f"Exception in main analyzer thread: {e}")

    def cleanup(self):
        """
        Clean up resources before shutting down.
        """
        self.logger.info("Stopping ChessCubeAnalyzer thread.")
        self.stop_event.set()
        self.obstacle_thread.join()  # Wait for the obstacle detection thread to finish
        self.join()  # Wait for the main thread to finish
        self.logger.info("Releasing webcam and cleaning up resources.")
        self.cap.release()
        self.processor.cleanup()
        cv2.destroyAllWindows()
