import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)


class Stepper:
    def __init__(self, number_of_steps: int, motor_pin_1: int, motor_pin_2: int, motor_pin_3: int, motor_pin_4: int):
        
        
        self.step_number = 0
        self.direction = 0
        self.last_step_time = 0
        self.number_of_steps = number_of_steps
        
        self.motor_pin_1 = motor_pin_1
        self.motor_pin_2 = motor_pin_2
        self.motor_pin_3 = motor_pin_3
        self.motor_pin_4 = motor_pin_4

        GPIO.setup(self.motor_pin_1, GPIO.OUT)
        GPIO.setup(self.motor_pin_2, GPIO.OUT)
        GPIO.setup(self.motor_pin_3, GPIO.OUT)
        GPIO.setup(self.motor_pin_4, GPIO.OUT)

        self.pin_count = 4

    def setSpeed(self, whatSpeed: int):

        self.step_delay = 60 * 1000 * 1000 / self.number_of_steps / whatSpeed

    #Moves the stepper motor "steps_to_move" number of times
    #Positive -> CW  Negative -> CCW
    def step(self, steps_to_move: int):
        
        steps_left:int = abs(steps_to_move)

        if(steps_to_move > 0):
            self.direction = 1
        if(steps_to_move < 0):
            self.direction = 0

        while(steps_left > 0):
            now:int = time.process_time_ns() / 1000

            if(now - self.last_step_time >= self.step_delay):
                self.last_step_time = now

                if(self.direction == 1):
                    self.step_number += 1

                    if(self.step_number == self.number_of_steps):
                        self.step_number = 0

                else:

                    if(self.step_number == 0):
                        self.step_number = self.number_of_steps
                    
                    self.step_number -= 1

                steps_left -= 1

                self.stepMotor(self.step_number % 4)

    #Controls the motor
    def stepMotor(self, this_step: int):
        #1010
        if this_step == 0:
                GPIO.output(self.motor_pin_1, True)
                GPIO.output(self.motor_pin_2, False)
                GPIO.output(self.motor_pin_3, True)
                GPIO.output(self.motor_pin_4, False)

        #0110
        elif this_step == 1:
                GPIO.output(self.motor_pin_1, False)
                GPIO.output(self.motor_pin_2, True)
                GPIO.output(self.motor_pin_3, True)
                GPIO.output(self.motor_pin_4, False)

        #0101
        elif this_step == 2:
                GPIO.output(self.motor_pin_1, False)
                GPIO.output(self.motor_pin_2, True)
                GPIO.output(self.motor_pin_3, False)
                GPIO.output(self.motor_pin_4, True)

        #1001
        elif this_step == 3:
                GPIO.output(self.motor_pin_1, True)
                GPIO.output(self.motor_pin_2, False)
                GPIO.output(self.motor_pin_3, False)
                GPIO.output(self.motor_pin_4, True)
    def close(self):
        GPIO.cleanup()
