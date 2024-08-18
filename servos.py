import RPi.GPIO as GPIO
import time

# Configuración de los pines GPIO
SERVO_MADURO_PIN = 12   # Cambia estos pines a los que estás usando
SERVO_DANADO_PIN = 23   # Cambia estos pines a los que estás usando
SERVO_BANDA_PIN = 25   # Cambia estos pines a los que estás usando

# Configuración de los servos
SERVO_MADURO_PWM_FREQ = 50
SERVO_DANADO_PWM_FREQ = 50
SERVO_BANDA_PWM_FREQ = 50

# Inicialización de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_MADURO_PIN, GPIO.OUT)
GPIO.setup(SERVO_DANADO_PIN, GPIO.OUT)
GPIO.setup(SERVO_BANDA_PIN, GPIO.OUT)

# Configuración de PWM para cada servo
servo_maduro_pwm = GPIO.PWM(SERVO_MADURO_PIN, SERVO_MADURO_PWM_FREQ)
servo_danado_pwm = GPIO.PWM(SERVO_DANADO_PIN, SERVO_DANADO_PWM_FREQ)
servo_banda_pwm = GPIO.PWM(SERVO_BANDA_PIN, SERVO_BANDA_PWM_FREQ)

servo_maduro_pwm.start(0)
servo_danado_pwm.start(0)
servo_banda_pwm.start(0)


def set_servo_angle(pwm, angle):
    duty_cycle = (angle / 18) + 2
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)

def servo_maduro():
    self.set_servo_angle(self.servo_maduro_pwm, 0)
    time.sleep(0.5)
    self.set_servo_angle(self.servo_danado_pwm, 87)
    time.sleep(4)
    self.set_servo_angle(self.servo_maduro_pwm, 0)
    time.sleep(0.5)


def servo_danado():
    set_servo_angle(servo_danado_pwm, 0)
    time.sleep(3)
    set_servo_angle(servo_danado_pwm, 87)
    time.sleep(3)
    set_servo_angle(servo_danado_pwm, 0)
    time.sleep(3)

#def servo_banda():
    # Los servos de 360 grados no se mueven a ángulos específicos, sino que giran continuamente
    # Cambiar el duty cycle para girar el servo de 360 grados en una dirección específica
    #servo_banda_pwm.ChangeDutyCycle(10)  
    #time.sleep(10)  # Esperar 3 segundos
    #servo_banda_pwm.ChangeDutyCycle(7)  # Detener el servo
    #time.sleep(3)
    #servo_banda_pwm.ChangeDutyCycle(10)  
    #time.sleep(5)  # Esperar 3 segundos

try:
    while True:

        #print("Moviendo servo maduro a 87 grados...")
        servo_maduro()
        time.sleep(2)
        
        #print("Moviendo servo dañado a 87 grados...")
        servo_danado()
        time.sleep(2)

        
        #print("Moviendo servo banda...")
        #servo_banda()
        #time.sleep(2)

except KeyboardInterrupt:
    print("Programa terminado por el usuario.")
finally:
    servo_maduro_pwm.stop()
    servo_danado_pwm.stop()
    #servo_banda_pwm.stop()
    GPIO.cleanup()


