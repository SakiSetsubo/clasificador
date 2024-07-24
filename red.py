from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
import time
import threading


def motor_podrito():
    semaphore.acquire()
    try:
        print("Encender motor podrido")
        time.sleep(4)
        print("Terminado motor posrido")
    finally:
        semaphore.release()


def motor_maduros():
    semaphore.acquire()
    try:
        print("Encender motor maduro")
        time.sleep(4)
        print("terminado motor maduro")
    finally:
        semaphore.release()


def verdes():
    semaphore.acquire()
    try:
        print("Limones verdes")
        time.sleep(4)
        print("terminado verde")
    finally:
        semaphore.release()


def red():
    # Disable scientific notation for clarity
    np.set_printoptions(suppress=True)

    # Load the model
    model = load_model("keras_Model.h5", compile=False)

    # Load the labels
    class_names = open("labels.txt", "r").readlines()

    # CAMERA can be 0 or 1 based on default camera of your computer
    camera = cv2.VideoCapture(0)

    vector = []

    while True:
        # Grab the webcamera's image.
        ret, image = camera.read()

        # Resize the raw image into (224-height,224-width) pixels
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Show the image in a window
        cv2.imshow("Webcam Image", image)

        # Make the image a numpy array and reshape it to the models input shape.
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

        # Normalize the image array
        image = (image / 127.5) - 1

        # Predicts the model
        prediction = model.predict(image)
        index = np.argmax(prediction)
        class_name = class_names[index]
        confidence_score = prediction[0][index]

        # Print prediction and confidence score
        # print("Class:", class_name[2:], end="")
        # print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

        # Tomar desiciones
        estado = class_name[2:].strip()
        # print(estado)

        if estado == "Nada":
            if len(vector) == 0:
                # print("Iniciando")
                a = 0
            else:
                if (
                    vector.count("Podrido") == 0
                    and vector.count("Maduro") == 0
                    and len(vector) > vector_len
                ):
                    threading.Thread(target=verdes).start()
                if (
                    vector.count("Verde") == 0
                    and vector.count("Maduro") == 0
                    and len(vector) > vector_len
                ):
                    threading.Thread(target=motor_podrito).start()
                if (
                    vector.count("Verde") == 0
                    and vector.count("podrido") == 0
                    and len(vector) > vector_len
                ):
                    threading.Thread(target=motor_maduros).start()
                vector = []
        else:
            vector.append(estado)
            # print("Agregando")

        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)

        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27:
            break
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    vector_len = 20
    semaphore = threading.Semaphore(1)
    main_thread = threading.Thread(target=red)
    main_thread.start()
    main_thread.join()
