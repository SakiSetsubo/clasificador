from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("keras_Model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

# CAMERA can be 0 or 1 based on default camera of your computer
camera = cv2.VideoCapture(0)

# Initialize the object tracker
tracker = cv2.legacy.TrackerCSRT_create()
initBB = None

while True:
    # Grab the webcamera's image.
    ret, frame = camera.read()

    if not ret:
        break

    # Perform object detection on the first frame or if tracking fails
    if initBB is None:
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply GaussianBlur to reduce noise and improve contour detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Perform edge detection
        edged = cv2.Canny(blurred, 50, 150)
        # Find contours
        contours, _ = cv2.findContours(
            edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if contours:
            # Find the largest contour by area
            c = max(contours, key=cv2.contourArea)
            (x, y, w, h) = cv2.boundingRect(c)
            initBB = (x, y, w, h)
            tracker.init(frame, initBB)

    # If tracking is initialized, update the tracker
    if initBB is not None:
        (success, box) = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Prepare image for classification
            image = cv2.resize(
                frame[y : y + h, x : x + w], (224, 224), interpolation=cv2.INTER_AREA
            )
            image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
            image = (image / 127.5) - 1

            # Predict the model
            prediction = model.predict(image)
            index = np.argmax(prediction)
            class_name = class_names[index]
            confidence_score = prediction[0][index]

            # Add label text below the rectangle
            label = (
                f"{class_name.strip()}: {str(np.round(confidence_score * 100))[:-2]}%"
            )
            cv2.putText(
                frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )
        else:
            initBB = None  # Stop tracking if tracking failed

    # Show the frame with the tracked object and label
    cv2.imshow("Tracking", frame)

    # Listen to the keyboard for presses
    keyboard_input = cv2.waitKey(1)

    # 27 is the ASCII for the esc key on your keyboard
    if keyboard_input == 27:
        break

camera.release()
cv2.destroyAllWindows()
