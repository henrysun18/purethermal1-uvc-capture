from gpiozero import TonalBuzzer
from gpiozero.tones import Tone
from gpiozero.tools import sin_values

import RPi.GPIO as GPIO
from time import sleep
import time

class Buzzer:
    def __init__(self, pin):
        self.buzzer = pin

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(buzzer, GPIO.OUT)

        self.delay = 0.8 # delay in seconds
        self.time_between_speedups = 3; # in seconds
        self.min_delay = 0.049 # delay in seconds

        self.time_since_speed_increase = time.time() #facilitate increasing speed of beeps

    def play(seconds):
        start_time = time.time()
        try:
            while True:
                current_time = time.time()
                print("current_time - time_since_speed_increase = ", current_time, " - ", time_since_speed_increase, " = ", int(current_time - time_since_speed_increase))
                if int(current_time - time_since_speed_increase) >= time_between_speedups:
                    delay = max(min_delay, delay/2)
                    time_since_speed_increase = current_time

                GPIO.output(buzzer, GPIO.HIGH)
                sleep(delay)
                GPIO.output(buzzer, GPIO.LOW)
                sleep(delay)

                if int(current_time - start_time > seconds):
                    break # stop playing after we played enough seconds as requested
        finally:
            GPIO.cleanup()


if __name__ == '__main__':
    Buzzer(7).play(30)
