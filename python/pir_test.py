import RPi.GPIO as GPIO
import time

pir_sensor = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir_sensor, GPIO.IN)

def present(pir_sensor):
    print("human is now present")

try:
    GPIO.add_event_detect(pir_sensor, GPIO.RISING, callback=present)
    while 1:
        time.sleep(100)
except KeyboardInterrupt:
	pass
finally:
	GPIO.cleanup()
