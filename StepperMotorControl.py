from Stepper import Stepper

stepsPerRevolution:int = 400

try:
    myStepper = Stepper(stepsPerRevolution, 29, 31, 33, 35)

    revs:int = 20
    counter: int = 0

    myStepper.setSpeed(100)

    while(True):
        myStepper.step(-stepsPerRevolution)
finally:
    myStepper.close()
