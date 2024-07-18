from keras.models import load_model
import cv2
import numpy as np

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("keras_Model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

# Initialize the tracker
tracker = cv2.TrackerKCF_create()

# CAMERA can be 0 or 1 based on default camera of your computer
camera = cv2.VideoCapture(0)

# Initialize variables
initBB = None
tracking = False

while True:
    # Grab the webcamera's image.
    ret, frame = camera.read(1)

    if not ret:
        print("Failed to grab frame")
        break

    # Resize the raw image into (224-height,224-width) pixels
    resized_frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)

    # Make the image a numpy array and reshape it to the model's input shape.
    image = np.asarray(resized_frame, dtype=np.float32).reshape(1, 224, 224, 3)

    # Normalize the image array
    image = (image / 127.5) - 1

    # Predicts the model
    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()
    confidence_score = prediction[0][index]

    # Print prediction and confidence score
    print("Class:", class_name, end="")
    print(" Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

    # Start tracking if confidence is high
    if confidence_score > 0.8 and not tracking:
        # Convert to grayscale for contour detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(
            gray, (5, 5), 0
        )  # Apply Gaussian blur to reduce noise
        _, thresh = cv2.threshold(blurred, 128, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if contours:
            largest_contour = max(
                contours, key=cv2.contourArea
            )  # Get the largest contour
            x, y, w, h = cv2.boundingRect(largest_contour)
            initBB = (x, y, w, h)
            tracker = cv2.TrackerKCF_create()  # Reinitialize the tracker
            tracker.init(frame, initBB)
            tracking = True
            print(f"Started tracking at: {initBB}")
        else:
            print("No contours found")

    if tracking:
        # Update the tracker
        success, box = tracker.update(frame)
        if success:
            x, y, w, h = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(
                frame,
                f"ID: 1 {class_name}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

            # Crop the detected object area from the frame
            cropped_frame = frame[y : y + h, x : x + w]
            if cropped_frame.size > 0:
                # Show the cropped image in a new window
                cv2.imshow("Cropped Object", cropped_frame)
            else:
                print("Cropped frame is empty")
        else:
            print("Tracking failed")
            tracking = False

    # Show the frame with tracking
    cv2.imshow("Tracked Webcam Image", frame)

    # Listen to the keyboard for presses.
    keyboard_input = cv2.waitKey(1) & 0xFF

    # 27 is the ASCII for the esc key on your keyboard.
    if keyboard_input == 27:
        break

camera.release()
cv2.destroyAllWindows()
