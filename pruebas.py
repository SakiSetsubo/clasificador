from keras.models import load_model  # TensorFlow es necesario para Keras
import cv2  # Instalar opencv-python
import numpy as np

# Deshabilitar la notación científica para mayor claridad
np.set_printoptions(suppress=True)

# Cargar el modelo
model = load_model("keras_Model.h5", compile=False)

# Cargar las etiquetas
class_names = open("labels.txt", "r").readlines()

# La cámara puede ser 0 o 1 dependiendo de la cámara predeterminada de tu computadora
camera = cv2.VideoCapture(0)

# Inicializar el seguidor de objetos
tracker = cv2.legacy.TrackerCSRT_create()
initBB = None
auto_select = True

while True:
    # Capturar la imagen de la cámara web
    ret, frame = camera.read()

    if auto_select and initBB is None:
        # Convertir el frame a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Aplicar GaussianBlur para reducir el ruido y mejorar la detección de contornos
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Realizar detección de bordes
        edged = cv2.Canny(blurred, 50, 150)
        # Encontrar contornos
        contours, _ = cv2.findContours(
            edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if contours:
            # Encontrar el contorno más grande por área
            c = max(contours, key=cv2.contourArea)
            (x, y, w, h) = cv2.boundingRect(c)
            initBB = (x, y, w, h)
            tracker.init(frame, initBB)
            auto_select = False

    if initBB is not None:
        (success, box) = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            initBB = None  # Dejar de seguir si falla el seguimiento

    # Redimensionar la imagen cruda a (224-altura, 224-ancho) píxeles para la clasificación
    image = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)

    # Mostrar el frame en una ventana
    cv2.imshow("Webcam Image", frame)

    # Convertir la imagen a un array de numpy y cambiar su forma para el modelo
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

    # Normalizar el array de la imagen
    image = (image / 127.5) - 1

    # Realizar predicción con el modelo
    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    # Imprimir la predicción y el puntaje de confianza
    print("Class:", class_name[2:], end="")
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

    # Mostrar el frame con el objeto seguido
    cv2.imshow("Tracking", frame)

    # Escuchar el teclado para presionar teclas
    keyboard_input = cv2.waitKey(1)

    # 27 es el código ASCII para la tecla esc en tu teclado
    if keyboard_input == 27:
        break

camera.release()
cv2.destroyAllWindows()
