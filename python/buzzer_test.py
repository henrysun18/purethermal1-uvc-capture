import RPi.GPIO as GPIO
import time

pir_sensor = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir_sensor, GPIO.IN)

try:
	while(True):
		print(GPIO.input(pir_sensor))
		time.sleep(0.2)
except KeyboardInterrupt:
	pass
finally:
	GPIO.cleanup()
