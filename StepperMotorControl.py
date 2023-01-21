import Stepper as Stepper

stepsPerRevolution:int = 400


MyStepper = Stepper(stepsPerRevolution, 29, 31, 33, 35)

revs:int = 20
counter: int = 0

MyStepper.setSpeed(100)

while(True):
    for i in range(0,20):
        MyStepper.step(-stepsPerRevolution)