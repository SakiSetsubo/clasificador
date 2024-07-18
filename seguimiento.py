from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("keras_Model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

# Initialize the tracker
tracker = cv2.TrackerCSRT_create()

# CAMERA can be 0 or 1 based on default camera of your computer
camera = cv2.VideoCapture(0)

# Initialize variables
initBB = None

while True:
    # Grab the webcamera's image.
    ret, frame = camera.read()

    if not ret:
        break

    # Resize the raw image into (224-height,224-width) pixels
    resized_frame = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)

    # Show the image in a window
    cv2.imshow("Webcam Image", resized_frame)

    # Make the image a numpy array and reshape it to the model's input shape.
    image = np.asarray(resized_frame, dtype=np.float32).reshape(1, 224, 224, 3)

    # Normalize the image array
    image = (image / 127.5) - 1

    # Predicts the model
    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    # Print prediction and confidence score
    print("Class:", class_name.strip(), end="")
    print(" Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

    if initBB is not None:
        # Update the tracker
        (success, box) = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(
                frame,
                f"ID: 1 {class_name.strip()}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )
        else:
            initBB = None

    # Show the frame with tracking
    cv2.imshow("Tracked Webcam Image", frame)

    # Listen to the keyboard for presses.
    keyboard_input = cv2.waitKey(1) & 0xFF

    # 's' key to start tracking
    if keyboard_input == ord("s"):
        initBB = cv2.selectROI(
            "Tracked Webcam Image", frame, fromCenter=False, showCrosshair=True
        )
        tracker.init(frame, initBB)

    # 27 is the ASCII for the esc key on your keyboard.
    if keyboard_input == 27:
        break

camera.release()
cv2.destroyAllWindows()
