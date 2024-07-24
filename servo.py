import RPi.GPIO as GPIO
import time

# Configuración del pin GPIO
servo_pin = 18

# Configurar el modo de numeración de pines
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# Configurar el PWM (Pulse Width Modulation) para el servomotor
pwm = GPIO.PWM(servo_pin, 50)  # Frecuencia en Hz (50 Hz para servomotores)
pwm.start(0)  # Inicializar el ciclo de trabajo en 0%

try:
    while True:
        # Mover el servomotor a 0 grados
        pwm.ChangeDutyCycle(2.5)  # 2.5% para 0 grados
        time.sleep(1)

        # Mover el servomotor a 90 grados
        pwm.ChangeDutyCycle(7.5)  # 7.5% para 90 grados
        time.sleep(1)

        # Mover el servomotor a 180 grados
        pwm.ChangeDutyCycle(12.5)  # 12.5% para 180 grados
        time.sleep(1)

except KeyboardInterrupt:
    pass

# Detener el PWM y limpiar la configuración
pwm.stop()
GPIO.cleanup()
