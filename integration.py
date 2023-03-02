import json
import time
import threading
from drone_client import DroneClient
import Stepper
from dai_red_object_detection import Vision


#MultiThread Updates for GCS :)
#https://stackoverflow.com/a/13151299
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

update = {"status": "In-Flight", "Current Location": {"Lat": 0, "Lng": 0, "Alt": 0}, "Current Heading": 360, "Current Speed": 0}

def update_gcs(update):
    json.dump(update)

RPM = 400

FIRE_PIN1 = 0
FIRE_PIN2 = 0
FIRE_PIN3 = 0
FIRE_PIN4 = 0
FIRE_SQUEEZE = 1000
FIRE_RELAX = -1000
FIRE_WAIT = 15 # seconds

EVAC_PIN1 = 0
EVAC_PIN2 = 0
EVAC_PIN3 = 0
EVAC_PIN4 = 0
EVAC_RELEASE = -1000
EVAC_RETURN = 1000
PAYLOAD_WAIT = 100 # seconds

TAKEOFF_HEIGHT = 20
current_height = TAKEOFF_HEIGHT

mission = True
command = None

drone = DroneClient("/dev/ttyTHS0", 57600)
drone.connect()
#drone.setGeoFence()
drone.armVehicle()
drone.takeoff(TAKEOFF_HEIGHT)

fire_servo = Stepper(RPM, FIRE_PIN1, FIRE_PIN2, FIRE_PIN3, FIRE_PIN4)
evac_servo = Stepper(RPM, EVAC_PIN1, EVAC_PIN2, EVAC_PIN3, EVAC_PIN4)

ug = RepeatedTimer(1, update_gcs, update)

fire_detector = Vision()

while(mission):
    #check for command message, using test command for now
    command = {"argType": "Evac", "lat": 35.300614, "long": -120.663356, "alt": current_height}

    # If not command received, update GCS and continue
    if (command == None):
        # GCS is Always Updating
        continue

    # Parse command received
    if (command.argType == "Evac"):
        drone.flyToCords(command.lat, command.lon, command.alt)
        # Call Winch Servo, start it up state
        evac_servo.step(EVAC_RELEASE)   # release the winch, CCW
        time.sleep(PAYLOAD_WAIT)                 # wait for payload
        evac_servo.step(EVAC_RETURN)         # return the winch, CW
    if (command.argType == "Fire"):
        drone.flyToCords(command.lat, command.lon, command.alt)
        # Identify and Extinguish Fire
        box = fire_detector.red_detection()
        # Wait for object to be detected
        while box == None:
            box = fire_detector.red_detection()
        # Call Fire Servo, starts in relaxed state
        fire_servo.step(FIRE_SQUEEZE)   # squeeze fire extinguisher
        time.sleep(FIRE_WAIT)                  # 7-15 seconds for exhuast
        fire_servo.step(FIRE_RELAX)     # relax fire extinguisher
    # GCS is Always Updating

#Land Home / "Return to Launch &/or Home"
drone.goHome()
#Stop GCS Update
ug.stop()
