import tkinter as tk
import cv2
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import time
import threading

# Variable global
running = False

class LemonClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CLASIFICADOR DE LIMONES")

        # Configuración de los pines GPIO y PWM
        self.SERVO_MADURO_PIN = 23
        self.SERVO_DANADO_PIN = 24
        self.SERVO_BANDA_PIN = 25
        self.SERVO_MADURO_PWM_FREQ = 50
        self.SERVO_DANADO_PWM_FREQ = 50
        self.SERVO_BANDA_PWM_FREQ = 50

        # Inicialización de GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SERVO_MADURO_PIN, GPIO.OUT)
        GPIO.setup(self.SERVO_DANADO_PIN, GPIO.OUT)
        GPIO.setup(self.SERVO_BANDA_PIN, GPIO.OUT)

        # Configuración de PWM para cada servo
        self.servo_maduro_pwm = GPIO.PWM(self.SERVO_MADURO_PIN, self.SERVO_MADURO_PWM_FREQ)
        self.servo_danado_pwm = GPIO.PWM(self.SERVO_DANADO_PIN, self.SERVO_DANADO_PWM_FREQ)
        self.servo_banda_pwm = GPIO.PWM(self.SERVO_BANDA_PIN, self.SERVO_BANDA_PWM_FREQ)

        self.servo_maduro_pwm.start(0)
        self.servo_danado_pwm.start(0)
        self.servo_banda_pwm.start(0)

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

        # Etiquetas para los contadores
        self.verdes_label = tk.Label(
            self.counter_frame,
            text="Verdes:",
            bg="gray",
            fg="white",
            font=("Arial", 12, "bold"),
            anchor=tk.W,
        )
        self.verdes_label.grid(row=0, column=0, sticky=tk.W, padx=20, pady=5)

        self.maduros_label = tk.Label(
            self.counter_frame,
            text="Maduros:",
            bg="gray",
            fg="white",
            font=("Arial", 12, "bold"),
            anchor=tk.W,
        )
        self.maduros_label.grid(row=1, column=0, sticky=tk.W, padx=20, pady=5)

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

        # Botones
        self.start_button = tk.Button(
            self.buttons_frame,
            text="Start",
            command=self.start_all,
            font=("Arial", 10),
            width=26,
            height=2,
        )
        self.start_button.pack(padx=5, pady=5)

        self.stop_button = tk.Button(
            self.buttons_frame,
            text="Stop",
            command=self.stop_all,
            font=("Arial", 10),
            width=26,
            height=2,
        )
        self.stop_button.pack(padx=5, pady=5)

        self.reset_button = tk.Button(
            self.buttons_frame,
            text="Reset",
            command=self.reset_counts,
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
        
        # Threading
        self.semaphore = threading.Semaphore(1)

    def start_camera(self):
        if not self.is_camera_running:
            self.camera = cv2.VideoCapture(0)  # Usar la cámara predeterminada
            self.is_camera_running = True
            self.update_camera()

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

    def stop_camera(self):
        if self.is_camera_running:
            self.camera.release()
            self.is_camera_running = False
            #self.servo_banda_pwm.ChangeDutyCycle(7) 

    def reset_counts(self):
        self.verdes_count = 0
        self.maduros_count = 0
        self.podridos_count = 0
        self.update_counters()

    def update_counters(self):
        self.verdes_count_var.set(f"{self.verdes_count:3d}")
        self.maduros_count_var.set(f"{self.maduros_count:3d}")
        self.podridos_count_var.set(f"{self.podridos_count:3d}")

    def classify_lemon(self, lemon_type):
        if lemon_type == "verde":
            self.verdes_count += 1
        elif lemon_type == "maduro":
            self.maduros_count += 1
        elif lemon_type == "podrido":
            self.podridos_count += 1
        self.update_counters()

    def set_servo_angle(pwm, angle):
        duty_cycle = (angle / 18) + 2
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(1)
        self.pwm.ChangeDutyCycle(0)
        
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
            
    # Desiciones banda 
    def start_banda(self):
        global running
        if not running:
            running = True
            servo_thread = threading.Thread(target=self.run_servo)
            servo_thread.start()
        #print("----------Servo started-------------")
        
    def stop_banda(self):
        global running
        running = False
        self.servo_banda_pwm.ChangeDutyCycle(7)
        #print("------------Servo stopped-----------")

    def run_servo(self):
        global running
        while running:
            #print("Corriendo servo")
            self.servo_banda_pwm.ChangeDutyCycle(10)
            #time.sleep(0.1)
                
    def start_all(self):
        self.start_banda()
        self.start_camera()
        self.set_servo_angle(self.servo_maduro_pwm, 87)
        time.sleep(1)
        
    def stop_all(self):
        self.stop_banda()
        self.stop_camera()
        self.set_servo_angle(self.servo_maduro_pwm, 0)
        

if __name__ == "__main__":

    root = tk.Tk()
    app = LemonClassifierApp(root)
    root.mainloop()
