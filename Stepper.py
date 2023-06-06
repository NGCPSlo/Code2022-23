import Jetson.GPIO as GPIO
import time

#jetson toggle delay
toggle_delay = 58
#usleep function delay, (non-linear, calibrate expirementally)
usleep_delay = 150
usleep = lambda x: time.sleep(x/1000000)

#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

class Stepper:
	def __init__(self, dir_pin: int, step_pin: int, slp_pin: int, rst_pin: int, enbl_pin: int, mode1_pin: int, mode2_pin: int, mode3_pin: int):
		self.dir_pin = dir_pin
		self.step_pin = step_pin
		self.slp_pin = slp_pin
		self.rst_pin = rst_pin
		self.enbl_pin = enbl_pin
		#self.mode1_pin = x
		#self.mode2_pin = x
		#self.mode3_pin = x
		
		GPIO.setup(self.dir_pin, GPIO.OUT)
		GPIO.setup(self.step_pin, GPIO.OUT)
		GPIO.setup(self.slp_pin, GPIO.OUT)
		GPIO.setup(self.rst_pin, GPIO.OUT)
		GPIO.setup(self.enbl_pin, GPIO.OUT)
		#GPIO.setup(self.mode1_pin, GPIO.OUT)
		#GPIO.setup(self.mode2_pin, GPIO.OUT)
		#GPIO.setup(self.mode3_pin, GPIO.OUT)

	def setSpeed(self, mode1: bool, mode2: bool, mode3: bool):
		### 000 = Full Step, 100 = Half Step, 010 = 1/4, 110 = 1/8, 001 = 1/16, else = 1/32
		#GPIO.output(mode1_pin, mode1);
		#GPIO.output(mode1_pin, mode1);
		#GPIO.output(mode1_pin, mode1);
		return 0

	def step(self, num_steps: int, direction: bool):
		#set and enable motor
		GPIO.output(self.dir_pin, direction) #clockwise vs counter
		GPIO.output(self.slp_pin, True)	# logical not, true here = false on board
		GPIO.output(self.rst_pin, True)	# logical not
		GPIO.output(self.enbl_pin, False)	# logical not

		#run motor
		for i in range(num_steps):
			GPIO.output(self.step_pin, True)
			usleep(330-toggle_delay-usleep_delay)
			GPIO.output(self.step_pin, False)
			usleep(330-toggle_delay-usleep_delay)

		#disable motor, MUST DO else DANGER
		GPIO.output(self.slp_pin, False)
		GPIO.output(self.rst_pin, False)
		GPIO.output(self.enbl_pin, True)

	#might not be safe, due to the remain disable when not running requirement above
	#the danger bug: an anonmylous attempt to run with no steps = infinite current, a.k.a. magic smoke
	def close(self):
		GPIO.cleanup()


if __name__ == "__main__":
	dir1_pin = 19
	step1_pin = 7
	slp1_pin = 11
	rst1_pin = 13
	enbl1_pin = 15

	dir2_pin = 37
	step2_pin = 35
	slp2_pin = 33
	rst2_pin = 31
	enbl2_pin = 29

	motor1 = Stepper(dir1_pin, step1_pin, slp1_pin, rst1_pin, enbl1_pin, 0, 0, 0)
	motor2 = Stepper(dir2_pin, step2_pin, slp2_pin, rst2_pin, enbl2_pin, 0, 0, 0)

	#motor1.step(20000, True) #fire extinguisher 15sec
	motor1.step(100000, False)
	#motor2.step(10000, True)
	#motor2.step(50000, False)#false = up for evac









