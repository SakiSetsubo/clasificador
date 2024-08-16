import tkinter as tk
import threading
import time

# Crear la ventana principal
root = tk.Tk()
root.title("Interfaz con Start y Stop")

# threading
running = False

# Funciones para los botones
def run_servo():
	global running
	while running:
		print("Corriendo servo")
		time.sleep(1)

def start_action():
	global running
	if not running:
		running = True
		servo_thread = threading.Thread(target=run_servo)
		servo_thread.start()
	print("----------Servo started-------------")

def stop_action():
	global running
	running = False
	print("------------Servo stopped-----------")

# Crear botones
start_button = tk.Button(root, text="Start", command=start_action, width=10)
stop_button = tk.Button(root, text="Stop", command=stop_action, width=10)

# Posicionar botones
start_button.pack(pady=10)
stop_button.pack(pady=10)

root.mainloop()

