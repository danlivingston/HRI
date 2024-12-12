# modules/utils.py
import cv2
import numpy as np

def draw_annotations(image, squares, cubes, cube_positions):
    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1
    text_color = (255, 255, 255)  # White
    text_outline = (0, 0, 0)      # Black for outline

    # Define chess columns
    columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    # Draw squares and labels
    for square in squares:
        x, y, w, h = square['x'], square['y'], square['w'], square['h']
        row, col = square['row'], square['col']

        # Draw square rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)

        # Determine square label
        square_label = f"{columns[col]}{8 - row}"  # e.g., 'A1', 'B2'

        # Calculate text size to center the label
        (text_width, text_height), _ = cv2.getTextSize(square_label, font, font_scale, font_thickness)
        text_x = x + (w - text_width) // 2
        text_y = y + (h + text_height) // 2

        # Add black outline for better visibility
        cv2.putText(image, square_label, (text_x, text_y), font, font_scale, text_outline, font_thickness + 2, cv2.LINE_AA)
        # Add white text
        cv2.putText(image, square_label, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        # If there are cubes on this square, annotate them
        if square_label in cube_positions:
            cube_colors = cube_positions[square_label].split(', ')
            for idx, cube_color in enumerate(cube_colors):
                annotation = f"{cube_color.capitalize()} Cube"

                # Position the annotations with slight vertical offsets to avoid overlap
                (anno_width, anno_height), _ = cv2.getTextSize(annotation, font, font_scale, font_thickness)
                anno_x = x + (w - anno_width) // 2
                anno_y = y + h - 5 - (idx * (anno_height + 5))  # Adjust vertical position

                # Add black outline
                cv2.putText(image, annotation, (anno_x, anno_y), font, font_scale, text_outline, font_thickness + 2, cv2.LINE_AA)
                # Add white text
                cv2.putText(image, annotation, (anno_x, anno_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

    return image

def map_cube_to_square(cube, squares):
    # Find the center of the cube
    center_x = cube['x'] + cube['w'] / 2
    center_y = cube['y'] + cube['h'] / 2

    # Determine which square this point falls into
    for square in squares:
        x, y, w, h = square['x'], square['y'], square['w'], square['h']
        if x <= center_x < x + w and y <= center_y < y + h:
            return square['row'], square['col']
    return None, None
