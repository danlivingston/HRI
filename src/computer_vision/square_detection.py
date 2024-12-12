# modules/square_detection.py
import cv2
import numpy as np

def warp_perspective(image, pts, size=(800, 800)):
    destination = np.array([
        [0, 0],
        [size[0] - 1, 0],
        [size[0] - 1, size[1] - 1],
        [0, size[1] - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(pts, destination)
    warped = cv2.warpPerspective(image, M, size)
    return warped, M

def detect_squares(image, debug=False, chessboard_size=(8, 8)):
    squares = []
    img_height, img_width = image.shape[:2]
    square_size_w = img_width / chessboard_size[0]
    square_size_h = img_height / chessboard_size[1]

    for row in range(chessboard_size[1]):
        for col in range(chessboard_size[0]):
            x = int(round(col * square_size_w))
            y = int(round(row * square_size_h))
            x_end = int(round((col + 1) * square_size_w))
            y_end = int(round((row + 1) * square_size_h))
            w = x_end - x
            h = y_end - y

            square = {
                'row': row,
                'col': col,
                'x': x,
                'y': y,
                'w': w,
                'h': h
            }
            squares.append(square)
            if debug:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.putText(image, f"{col},{row}", (x + 5, y + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    if debug:
        cv2.imshow("Detected Squares", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return squares


