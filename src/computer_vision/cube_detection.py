import cv2
import numpy as np
import os

def detect_cubes(image, config, debug=False):
    # Increase saturation
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = cv2.add(s, 50)  # Increase saturation by 50, adjust this value as needed
    saturated_hsv = cv2.merge([h, s, v])
    saturated_image = cv2.cvtColor(saturated_hsv, cv2.COLOR_HSV2BGR)


    # Save the saturated image if debug is enabled
    if debug:
        output_folder = 'debug_images'
        os.makedirs(output_folder, exist_ok=True)
        cv2.imwrite(os.path.join(output_folder, "saturated_image2.jpg"), saturated_image)

    # Use saturated image for cube detection
    bgr = saturated_image  # Use the modified image

    # Initialize masks for blue and brown
    mask_blue = np.zeros(image.shape[:2], dtype="uint8")
    mask_brown = np.zeros(image.shape[:2], dtype="uint8")

    # Process blue ranges
    for range_set in config['cube_detection']['blue']['rgb_ranges']:
        lower = np.array(range_set['lower'], dtype="uint8")
        upper = np.array(range_set['upper'], dtype="uint8")
        current_mask = cv2.inRange(bgr, lower, upper)
        mask_blue = cv2.bitwise_or(mask_blue, current_mask)

    # Process brown ranges
    for range_set in config['cube_detection']['brown']['rgb_ranges']:
        lower = np.array(range_set['lower'], dtype="uint8")
        upper = np.array(range_set['upper'], dtype="uint8")
        current_mask = cv2.inRange(bgr, lower, upper)
        mask_brown = cv2.bitwise_or(mask_brown, current_mask)

    # Apply morphological operations to reduce noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel, iterations=2)
    mask_brown = cv2.morphologyEx(mask_brown, cv2.MORPH_OPEN, kernel, iterations=2)

    if debug:
        # Display the masks for blue and brown
        cv2.imshow("Blue Mask", mask_blue)
        cv2.imshow("Brown Mask", mask_brown)

    # Find contours for blue and brown cubes
    cubes = []
    for mask, color in zip([mask_blue, mask_brown], ['blue', 'brown']):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > config['thresholds']['cube_area_min']:  # Check if the area is large enough
                x, y, w, h = cv2.boundingRect(cnt)

                # Now, instead of checking if the aspect ratio is square-like, we only check the size
                if w >= config['thresholds']['cube_width_min'] and h >= config['thresholds']['cube_height_min']:
                    cube = {'color': color, 'x': x, 'y': y, 'w': w, 'h': h}
                    cubes.append(cube)
                    if debug:
                        # Define color for rectangle: Blue or Orange (for better visibility)
                        color_bgr = (255, 0, 0) if color == 'blue' else (0, 165, 255)
                        cv2.rectangle(image, (x, y), (x + w, y + h), color_bgr, 2)

    if debug:
        cv2.imshow("Cubes Detection", image)
        cv2.waitKey(0)

    return cubes
