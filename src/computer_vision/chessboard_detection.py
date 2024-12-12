
import os
from datetime import datetime
from typing import List, Tuple

import cv2
import numpy as np

def cut_image_corners(image, points, debug=False):
    """
    Makes areas outside a specified quadrilateral in the input image white.

    :param image: Input image as a NumPy array.
    :param points: A list or array of four points defining the quadrilateral (in clockwise or counterclockwise order).
                   Example: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    :param debug: If True, displays and saves the masked image.
    :return: Image with areas outside the quadrilateral set to white.
    """
    # Validate input points
    if len(points) != 4:
        raise ValueError("You must provide exactly 4 points to define the quadrilateral.")

    # Create a mask with the same dimensions as the input image
    height, width = image.shape[:2]
    mask = np.zeros((height, width), dtype="uint8")

    # Convert points to integer for drawing
    points = np.array(points, dtype=np.int32)

    # Draw a filled white quadrilateral on the mask
    cv2.fillPoly(mask, [points], 255)

    # If the image is colored (BGR), create a 3-channel mask
    if len(image.shape) == 3 and image.shape[2] == 3:
        mask_stack = np.stack([mask] * 3, axis=-1)
        white_background = np.full_like(image, 255)  # Create a white background
        masked_image = np.where(mask_stack == 255, image, white_background)
    else:
        # For grayscale images
        white_background = np.full_like(image, 255)  # Create a white background
        masked_image = np.where(mask == 255, image, white_background)


    return masked_image

def order_points(pts):
    """
    Orders points in the following order: top-left, top-right, bottom-right, bottom-left.

    :param pts: A list of four points (tuples) representing the quadrilateral.
    :return: Ordered numpy array of points.
    """
    rect = np.zeros((4, 2), dtype="float32")

    # Convert to numpy array
    pts = np.array(pts, dtype="float32")

    # The top-left point will have the smallest sum,
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # Compute the difference between the points
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect

def detect_chessboard_border(predefined_points: List[Tuple[int, int]], image, debug=False) -> np.ndarray:
    """
    Returns the predefined quadrilateral points ordered as top-left, top-right, bottom-right, bottom-left.

    :param predefined_points: List of four (x, y) tuples defining the quadrilateral.
    :param image: The original image (used only for debugging purposes).
    :param debug: If True, displays and saves the ordered points on the image.
    :return: Ordered numpy array of points.
    """
    if len(predefined_points) != 4:
        raise ValueError("Exactly four predefined points are required.")

    ordered_points = order_points(predefined_points)

    return ordered_points