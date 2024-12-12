import cv2

# Initialize the webcam (0 is the default camera)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture image.")
        break

    # Display the resulting frame
    cv2.imshow('Webcam Feed', frame)

    # Press 'q' to exit the webcam window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
