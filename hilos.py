import threading
import time


# Función que se ejecuta constantemente
def main_function():
    while True:
        print("Ejecutando la función principal...")
        # Aquí puedes poner tu lógica principal
        time.sleep(1)  # Simula un trabajo continuo

        # Condición para lanzar una tarea en paralelo
        if some_condition():
            threading.Thread(target=parallel_function).start()


# Función que se ejecuta en paralelo
def parallel_function():
    print("Ejecutando una tarea en paralelo...")
    # Aquí puedes poner la lógica que se ejecutará en paralelo
    time.sleep(5)  # Simula una tarea que toma tiempo
    print("Terminado")


# Condición de ejemplo
def some_condition():
    # Aquí puedes poner una condición para decidir cuándo lanzar la tarea en paralelo
    # Por ejemplo, lanzar una tarea cada 10 segundos
    return time.time() % 10 < 1


# Inicia la ejecución de la función principal en un hilo
main_thread = threading.Thread(target=main_function)
main_thread.start()

# Mantén el programa principal ejecutándose
main_thread.join()
