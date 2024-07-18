import threading
import time


def motor_1():
    time.sleep(2)
    print("Motor 1")


def motor_2():
    time.sleep(2)
    print("Motor 2")


def motor_banda():
    print("Ejecutando")


if __name__ == "__main__":

    banda = threading.Thread(target=motor_banda)
    banda.start()
    banda.join()


"""
    threads = []
    for i in range(1, 20):
        thread = threading.Thread(target=contar, args=(i,))
        thread.start()
        threads.append(thread)
        time.sleep(2)

    for thread in threads:
        thread.join()

    print("Finnalizado")
"""
