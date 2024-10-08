import tkinter as tk  # Libreria para la interfaz grafica
from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # LIbreria para utilizar la camara
import numpy as np  # Libreria para hacer operaciones con las imagenes
import time
import threading  # Libreria para manejar hilos
from PIL import Image, ImageTk  # LIbreria par la interfaz grafica


# Se crea la clase LemonClassifierApp
class LemonClassifierApp:
    def __init__(self, root):
        ### ATRIBUTOS

        # Atrubutos para la interfaz
        self.root = root
        self.root.title("CLASIFICADOR DE LIMONES")

        # Frame principal
        self.main_frame = tk.Frame(self.root, bg="gray")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Título de la interfaz
        self.title_label = tk.Label(
            self.main_frame,
            text="CLASIFICADOR DE LIMONES",
            font=("Arial", 18, "bold"),
            bg="gray",
            fg="white",
        )
        self.title_label.pack(pady=10, anchor=tk.N)

        # Frame para la cámara (lado izquierdo)
        self.camera_frame = tk.Frame(self.main_frame, width=224, height=224, bg="black")
        self.camera_frame.pack(side=tk.LEFT, padx=40, pady=10)

        # Frame para los contadores (lado derecho)
        self.counter_frame = tk.Frame(self.main_frame, width=341, height=600, bg="gray")
        self.counter_frame.pack(side=tk.RIGHT, padx=40, pady=10, fill=tk.Y)

        # Contadores
        self.verdes_count = 0
        self.maduros_count = 0
        self.podridos_count = 0

        # Etiqueta para el contador Verdes
        self.verdes_label = tk.Label(
            self.counter_frame,
            text="Verdes:",
            bg="gray",
            fg="white",
            font=("Arial", 12, "bold"),
            anchor=tk.W,
        )
        self.verdes_label.grid(row=0, column=0, sticky=tk.W, padx=20, pady=5)

        # Etiqueta para el contador Maduros
        self.maduros_label = tk.Label(
            self.counter_frame,
            text="Maduros:",
            bg="gray",
            fg="white",
            font=("Arial", 12, "bold"),
            anchor=tk.W,
        )
        self.maduros_label.grid(row=1, column=0, sticky=tk.W, padx=20, pady=5)

        # Etiqueta para el contador Podridos
        self.podridos_label = tk.Label(
            self.counter_frame,
            text="Podridos:",
            bg="gray",
            fg="white",
            font=("Arial", 12, "bold"),
            anchor=tk.W,
        )
        self.podridos_label.grid(row=2, column=0, sticky=tk.W, padx=20, pady=5)

        # Cajas para los números de contadores
        self.verdes_count_var = tk.StringVar()
        self.verdes_count_var.set("0")
        self.verdes_count_label = tk.Label(
            self.counter_frame,
            textvariable=self.verdes_count_var,
            bg="white",
            fg="black",
            font=("Arial", 12),
            width=10,
            anchor=tk.E,
            relief=tk.RIDGE,
        )
        self.verdes_count_label.grid(row=0, column=1, sticky=tk.E, padx=20, pady=5)

        self.maduros_count_var = tk.StringVar()
        self.maduros_count_var.set("0")
        self.maduros_count_label = tk.Label(
            self.counter_frame,
            textvariable=self.maduros_count_var,
            bg="white",
            fg="black",
            font=("Arial", 12),
            width=10,
            anchor=tk.E,
            relief=tk.RIDGE,
        )
        self.maduros_count_label.grid(row=1, column=1, sticky=tk.E, padx=20, pady=5)

        self.podridos_count_var = tk.StringVar()
        self.podridos_count_var.set("0")
        self.podridos_count_label = tk.Label(
            self.counter_frame,
            textvariable=self.podridos_count_var,
            bg="white",
            fg="black",
            font=("Arial", 12),
            width=10,
            anchor=tk.E,
            relief=tk.RIDGE,
        )
        self.podridos_count_label.grid(row=2, column=1, sticky=tk.E, padx=20, pady=5)

        # Crear un frame para los botones
        self.buttons_frame = tk.Frame(self.counter_frame, bg="gray")
        self.buttons_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.NSEW)

        # Boton Start
        self.start_button = tk.Button(
            self.buttons_frame,
            text="Start",
            command=self.start_camera,  # Ejecutar el metodo start_camera
            font=("Arial", 10),
            width=26,
            height=2,
        )
        self.start_button.pack(padx=5, pady=5)

        # Boton Stop
        self.stop_button = tk.Button(
            self.buttons_frame,
            text="Stop",
            command=self.stop_camera,  # Ejecutar el metodo stop_camera
            font=("Arial", 10),
            width=26,
            height=2,
        )
        self.stop_button.pack(padx=5, pady=5)

        # Boton Reset
        self.reset_button = tk.Button(
            self.buttons_frame,
            text="Reset",
            command=self.reset_counts,  # Ejecutar el metodo reset_counts
            font=("Arial", 10),
            width=26,
            height=2,
        )
        self.reset_button.pack(padx=5, pady=5)

        # Variable para la imagen de la cámara
        self.camera_image = None

        # Variables para control de la cámara
        self.camera = None
        self.is_camera_running = False

        # Modelo de clasificación y etiquetas
        self.model = None
        self.class_names = None
        self.vector = []
        self.vector_len = 20
        self.semaphore = threading.Semaphore(1)

    ### METODOS

    # Metodo para hacer funcionar la camara
    def start_camera(self):
        if not self.is_camera_running:
            self.camera = cv2.VideoCapture(0)  # Usar la cámara predeterminada
            self.is_camera_running = True
            self.update_camera()  # Llamar al metodo update_camera
            self.start_classification()

    # Metodo para refrescarla camara
    def update_camera(self):
        if self.is_camera_running:
            ret, frame = self.camera.read()
            if ret:
                # Ajustar tamaño sin deformar la imagen
                height, width, _ = frame.shape
                aspect_ratio = width / height
                target_width = 224  # Ancho deseado del frame de la cámara
                target_height = int(target_width / aspect_ratio)
                frame = cv2.resize(frame, (target_width, target_height))

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                # Si la etiqueta de la cámara no está creada, crearla
                if not hasattr(self, "camera_label"):
                    self.camera_label = tk.Label(self.camera_frame)
                    self.camera_label.pack()

                self.camera_label.configure(image=imgtk)
                self.camera_label.image = imgtk
                self.root.after(10, self.update_camera)  # Actualizar cada 10ms

    # Ejecutar run.clasification como un hilo
    def start_classification(self):
        threading.Thread(target=self.run_classification).start()

    # Ejecutar la clasificacion utilizando la red
    def run_classification(self):
        # Cargar el modelo y las etiquetas
        np.set_printoptions(suppress=True)
        self.model = load_model("keras_model.h5", compile=False)
        self.class_names = open("labels.txt", "r").readlines()

        while self.is_camera_running:
            ret, image = self.camera.read()
            if ret:
                image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
                image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
                image = (image / 127.5) - 1

                prediction = self.model.predict(image)
                index = np.argmax(prediction)
                class_name = self.class_names[index]
                confidence_score = prediction[0][index]

                estado = class_name[2:].strip()

                if estado == "Nada":
                    if len(self.vector) == 0:
                        print("Iniciando")
                    else:
                        if (
                            self.vector.count("Podrido") == 0
                            and self.vector.count("Maduro") == 0
                            and len(self.vector) > self.vector_len
                        ):
                            threading.Thread(target=self.verdes).start()
                        if (
                            self.vector.count("Verde") == 0
                            and self.vector.count("Maduro") == 0
                            and len(self.vector) > self.vector_len
                        ):
                            threading.Thread(target=self.motor_podrito).start()
                        if (
                            self.vector.count("Verde") == 0
                            and self.vector.count("podrido") == 0
                            and len(self.vector) > self.vector_len
                        ):
                            threading.Thread(target=self.motor_maduros).start()
                        self.vector = []
                else:
                    self.vector.append(estado)
                    print("Agregando")

    # Metodo para detener la camera
    def stop_camera(self):
        if self.is_camera_running:
            self.camera.release()
            self.is_camera_running = False

    # Metodo para resetear los contadores
    def reset_counts(self):
        self.verdes_count = 0
        self.maduros_count = 0
        self.podridos_count = 0
        self.update_counters()

    # Metodo para ir acutalizando los contadores
    def update_counters(self):
        self.verdes_count_var.set(f"{self.verdes_count:3d}")
        self.maduros_count_var.set(f"{self.maduros_count:3d}")
        self.podridos_count_var.set(f"{self.podridos_count:3d}")

    # Metodo para ir aumentando los contadores segun lo determine la red
    def classify_lemon(self, lemon_type):
        if lemon_type == "verde":
            self.verdes_count += 1
        elif lemon_type == "maduro":
            self.maduros_count += 1
        elif lemon_type == "podrido":
            self.podridos_count += 1
        self.update_counters()

    # Encender el motor para limones podridos
    def motor_podrito(self):
        self.semaphore.acquire()
        try:
            print("Encender motor podrido")
            time.sleep(4)
            print("Terminado motor podrido")
        finally:
            self.semaphore.release()

    # Encender el motor para limones maduros
    def motor_maduros(self):
        self.semaphore.acquire()
        try:
            print("Encender motor maduro")
            time.sleep(4)
            print("Terminado motor maduro")
        finally:
            self.semaphore.release()

    # Desiciones al tener limones verdes
    def verdes(self):
        self.semaphore.acquire()
        try:
            print("Limones verdes")
            time.sleep(4)
            print("Terminado verde")
        finally:
            self.semaphore.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = LemonClassifierApp(root)
    root.mainloop()
