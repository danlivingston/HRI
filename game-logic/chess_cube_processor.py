# chess_cube_processor.py

import os
import cv2
import numpy as np
import yaml
import logging
from typing import Optional, Dict, Any, Tuple, List

from modules.chessboard_detection import detect_chessboard_border, cut_image_corners, order_points
from modules.cube_detection import detect_cubes  # Your existing detect_cubes function
from modules.square_detection import detect_squares, warp_perspective


def draw_annotations(image, squares, cubes, cube_positions_str):
    columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    for square in squares:
        x, y, w, h = square['x'], square['y'], square['w'], square['h']
        row, col = square['row'], square['col']
        square_name = f"{columns[col]}{8 - row}"
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.putText(image, square_name, (x + 5, y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        # Annotate cubes on the squares
        if square_name in cube_positions_str:
            colors = cube_positions_str[square_name]
            color_text = colors
            cv2.putText(image, color_text, (x + 5, y + h - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    # Draw cubes
    for cube in cubes:
        x, y, w, h = cube['x'], cube['y'], cube['w'], cube['h']
        color_bgr = (255, 0, 0) if cube['color'] == 'blue' else (0, 165, 255)
        cv2.rectangle(image, (x, y), (x + w, y + h), color_bgr, 2)
    return image


def map_cube_to_square(cube, squares):
    cube_x, cube_y, cube_w, cube_h = cube['x'], cube['y'], cube['w'], cube['h']
    cube_center = (cube_x + cube_w / 2, cube_y + cube_h / 2)

    for square in squares:
        x, y, w, h = square['x'], square['y'], square['w'], square['h']
        if x <= cube_center[0] <= x + w and y <= cube_center[1] <= y + h:
            return square['row'], square['col']
    return None, None


class ChessCubeProcessor:
    def __init__(self, config_path: str = None,
                 debug: bool = False,
                 chessboard_points: Optional[List[Tuple[int, int]]] = None,
                 obstacle_detection_points: Optional[List[Tuple[int, int]]] = None):

        # Determine the path to the configuration file
        if config_path is None:
            # Use a relative path to the 'resources/config/settings.yaml' file
            config_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'config', 'settings.yaml')
        else:
            # If config_path is not absolute, make it relative to this file
            if not os.path.isabs(config_path):
                config_path = os.path.join(os.path.dirname(__file__), config_path)

        # Resolve the absolute path
        config_path = os.path.abspath(config_path)

        # Load the configuration
        self.config = self.load_config(config_path)
        self.debug = debug
        self.setup_logging()
        logging.info("ChessCubeProcessor initialized.")

        # Initialize points lists
        if chessboard_points is None:
            # Default chessboard points from config
            self.chessboard_points = [tuple(point) for point in self.config.get('chessboard_points', [(709, 286), (1171, 276), (1327, 830), (632, 855)])]
        else:
            self.chessboard_points = chessboard_points

        if obstacle_detection_points is None:
            # Default obstacle detection points from config
            self.obstacle_detection_points = [tuple(point) for point in self.config.get('obstacle_detection_points', [(600, 250), (1250, 250), (1250, 900), (600, 900)])]
        else:
            self.obstacle_detection_points = obstacle_detection_points

        # Initialize obstacle detection attributes
        self.reference_gray = None
        self.obstacle_initialized = False
        self.DIFF_THRESHOLD = self.config.get('line_deviation_threshold', 20)
        self.PERCENT_THRESHOLD = 0.02
        self.UPDATE_INTERVAL = self.config.get('initialization_frames', 30)
        self.frame_count = 0

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.debug(f"Configuration loaded from {config_path}.")
        return config

    @staticmethod
    def rotate_image(image: Any, angle: int) -> Any:
        if angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == -90:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)
        else:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h))
            return rotated

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        if self.debug:
            logging.info("Debug mode is enabled.")

    def set_debug(self, debug: bool):
        self.debug = debug
        logging.getLogger().setLevel(logging.DEBUG if self.debug else logging.INFO)
        logging.info(f"Debug mode set to {self.debug}.")

    def initialize_obstacle_detection(self, image: Any):
        masked_image = cut_image_corners(image, self.obstacle_detection_points, debug=self.debug)
        reference_gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
        reference_gray = cv2.GaussianBlur(reference_gray, (5, 5), 0)
        self.reference_gray = reference_gray
        self.obstacle_initialized = True
        logging.info("Obstacle detection initialized with reference frame.")


    def detect_obstacle(self, image: Any) -> bool:
        if not self.obstacle_initialized:
            logging.error("Obstacle detection not initialized.")
            return False

        masked_image = cut_image_corners(image, self.obstacle_detection_points, debug=self.debug)
        current_gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.GaussianBlur(current_gray, (5, 5), 0)

        frame_diff = cv2.absdiff(self.reference_gray, current_gray)
        _, thresh = cv2.threshold(frame_diff, self.DIFF_THRESHOLD, 255, cv2.THRESH_BINARY)

        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        thresh = cv2.dilate(thresh, kernel, iterations=1)

        changed_pixels = np.sum(thresh > 0)
        total_pixels = thresh.size
        change_ratio = changed_pixels / total_pixels


        if change_ratio > self.PERCENT_THRESHOLD:
            logging.info("Obstacle detected!")
            return True

        self.frame_count += 1
        if self.frame_count % self.UPDATE_INTERVAL == 0:
            self.reference_gray = current_gray.copy()
            logging.info("Reference frame updated.")

        return False

    # New method to preprocess the image (increase saturation)
    @staticmethod
    def preprocess_image(image: Any, increase_value: int = 50) -> Any:
        # Convert from BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Split the channels
        h, s, v = cv2.split(hsv)
        # Increase saturation
        s = cv2.add(s, increase_value)
        # Limit the values to [0, 255]
        s = np.clip(s, 0, 255)
        # Merge back the channels
        hsv_enhanced = cv2.merge([h, s, v])
        # Convert back to BGR
        saturated_image = cv2.cvtColor(hsv_enhanced, cv2.COLOR_HSV2BGR)
        return saturated_image

    def process_image(self, image: Any, image_name: str, debug: Optional[bool] = None, skip_border_detection: bool = False) -> Tuple[bool, Optional[Dict[str, str]]]:
        if debug is not None:
            current_debug = debug
        else:
            current_debug = self.debug

        try:
            if image is None:
                logging.error(f"Received empty image for {image_name}.")
                return False, None

            if not skip_border_detection:
                # Obstacle detection code here if needed
                pass  # Assuming you handle this as per your requirements

            # Use the chessboard points from the configuration
            chessboard_points = np.array(self.chessboard_points, dtype='float32')
            ordered_points = order_points(chessboard_points)

            # Warp perspective to get a top-down view
            warped_size = tuple(self.config.get('warped_size', [800, 800]))
            warped_image, _ = warp_perspective(image, ordered_points, size=warped_size)

            if current_debug:
                cv2.imshow("Warped Image", warped_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            # Rotate the warped image if necessary
            rotation_angle = self.config.get('rotation_angle', -90)
            if rotation_angle != 0:
                warped_image = self.rotate_image(warped_image, rotation_angle)
                if current_debug:
                    cv2.imshow("Rotated Warped Image", warped_image)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

            # Preprocess the image (increase saturation)
            preprocessed_image = self.preprocess_image(warped_image, increase_value=50)
            if current_debug:
                cv2.imshow("Preprocessed Image", preprocessed_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            # Conditionally save the preprocessed image used for cube detection
            if current_debug:
                # Save the preprocessed image used for cube detection
                preprocessed_image_dir = os.path.join('preprocessed_images')
                os.makedirs(preprocessed_image_dir, exist_ok=True)
                preprocessed_image_path = os.path.join(preprocessed_image_dir, f"preprocessed_{image_name}")
                cv2.imwrite(preprocessed_image_path, preprocessed_image)
                logging.info(f"Preprocessed image saved as {preprocessed_image_path}")

            # Detect cubes on the preprocessed image
            # Optionally save the image used for color detection
            if current_debug:
                color_detection_image_path = os.path.join('debug_images', 'color_detection_image.jpg')
                os.makedirs(os.path.dirname(color_detection_image_path), exist_ok=True)
                cv2.imwrite(color_detection_image_path, preprocessed_image)
                logging.info(f"Image used for color detection saved as {color_detection_image_path}")

            # Use your existing detect_cubes function
            cubes = detect_cubes(preprocessed_image.copy(), self.config, debug=current_debug)

            if not cubes:
                logging.info(f"No cubes detected in {image_name}.")
                return False, None

            # Detect squares on the warped image
            chessboard_size = tuple(self.config.get('chessboard_size', [8, 8]))
            squares = detect_squares(warped_image.copy(), debug=current_debug, chessboard_size=chessboard_size)

            if squares is None or len(squares) != chessboard_size[0] * chessboard_size[1]:
                logging.error(f"Squares not properly detected in {image_name}.")
                return False, None

            logging.info(f"Number of squares detected: {len(squares)}")

            # Map cubes to squares
            cube_positions = {}
            for cube in cubes:
                row, col = map_cube_to_square(cube, squares)
                if row is not None and col is not None:
                    columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
                    square_label = f"{columns[col]}{8 - row}"
                    if square_label not in cube_positions:
                        cube_positions[square_label] = []
                    cube_positions[square_label].append(cube['color'])

            # Convert list of colors to a single string if multiple cubes are present
            cube_positions_str = {k: ', '.join(v) for k, v in cube_positions.items()}

            logging.info(f"Cubes on {image_name}: {cube_positions_str}")

            # Draw annotations on the warped image
            annotated = draw_annotations(warped_image.copy(), squares, cubes, cube_positions_str)

            if current_debug:
                cv2.imshow("Final Annotated Image", annotated)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            # Optionally, save the annotated image
            if current_debug:
                annotated_dir = os.path.join('annotated_images')
                os.makedirs(annotated_dir, exist_ok=True)
                annotated_path = os.path.join(annotated_dir, f"annotated_{image_name}")
                cv2.imwrite(annotated_path, annotated)
                logging.info(f"Annotated image saved to {annotated_path}")

            return False, cube_positions_str

        except Exception as e:
            logging.error(f"Error processing {image_name}: {e}")
            return False, None

    def cleanup(self):
        cv2.destroyAllWindows()
