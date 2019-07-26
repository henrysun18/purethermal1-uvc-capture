import RPi.GPIO as GPIO
from time import sleep
import time

class Buzzer:
    def __init__(self, pin):
        self.buzzer = pin
        self.enable = True

        self.starting_delay = 0.8 # delay in seconds
        self.time_between_speedups = 3; # in seconds
        self.min_delay = 0.049 # delay in seconds

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.buzzer, GPIO.OUT)

    def play(self, seconds):
        self.enable = True
        
        delay = self.starting_delay
        start_time = time.time()
        time_since_speed_increase = time.time() #facilitate increasing speed of beeps
        while True:
            current_time = time.time()
            print("current_time - time_since_speed_increase = ", current_time, " - ", time_since_speed_increase, " = ", int(current_time - time_since_speed_increase))
            if int(current_time - time_since_speed_increase) >= self.time_between_speedups:
                delay = max(self.min_delay, delay/2)
                time_since_speed_increase = current_time
            GPIO.output(self.buzzer, GPIO.HIGH)
            sleep(delay)
            GPIO.output(self.buzzer, GPIO.LOW)
            sleep(delay)

            if not self.enable or int(current_time - start_time > seconds):
                break 
    def stop(self, pin):
        self.enable = False

if __name__ == '__main__':
    Buzzer(7).play(30)
