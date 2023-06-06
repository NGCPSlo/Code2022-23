#!/bin/env python3.10
import json
import time
import request_client
from drone_client import DroneClient
from Stepper import Stepper
from dai_red_object_detection import Vision
from collections import deque
# udp:localhost:14551 for simulation
# /dev/ttyTHS1 for UART
drone = DroneClient("/dev/ttyTHS1", 57600)

'''
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
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
'''

def update_gcs(drone, ip_address, port):
    currentLocation = {'lat':drone.getCoords().lat,'lng':drone.getCoords().lon}
    request_client.send_cords(ip_address, "post_current", currentLocation, port)
    # call 



def main():
    update = {"status": "In-Flight", "Current Location": {"Lat": 0, "Lng": 0, "Alt": 0}, "Current Heading": 360, "Current Speed": 0}

    RPM = 400

    FIRE_dir_pin = 19
    FIRE_step_pin = 7
    FIRE_slp_pin = 11
    FIRE_rst_pin = 13
    FIRE_enbl_pin = 15
    FIRE_steps = 25000
    FIRE_steps1 = 5000
    FIRE_steps2 = 1000
    FIRE_WAIT = 15 # seconds

    EVAC_dir_pin = 37
    EVAC_step_pin = 35
    EVAC_slp_pin = 33
    EVAC_rst_pin = 31
    EVAC_enbl_pin = 29
    EVAC_steps = 80000
    PAYLOAD_WAIT = 20 # seconds, 300 is 5min

    TAKEOFF_HEIGHT = 3.5
    current_height = TAKEOFF_HEIGHT

    mission = True
    command = None

    print("Connecting Drone")
    drone.connect()
    #drone.setGeoFence()

    updateArgs = [drone,"localhost", 5000]
    
    #ug = RepeatedTimer(1, update_gcs, *updateArgs)
    drone.armVehicle()
    drone.takeoff(TAKEOFF_HEIGHT)
    #drne.goHome()
    #print("home")
    #return
    print("Connecting Motors")
    fire_servo = Stepper(FIRE_dir_pin, FIRE_step_pin, FIRE_slp_pin, FIRE_rst_pin, FIRE_enbl_pin, 0, 0 ,0)
    evac_servo = Stepper(EVAC_dir_pin, EVAC_step_pin, EVAC_slp_pin, EVAC_rst_pin, EVAC_enbl_pin, 0, 0, 0)

    print("Connecting Vision")
    fire_detector = Vision()
    #evac_servo.step(EVAC_steps, False)         # return the winch, CW

    print("Arming")
    #drone.armVehicle()
    print("Taking Off")
    #drone.takeoff(TAKEOFF_HEIGHT)

    # command = {"argType": "Evac", "lat": 35.300614, "lon": -120.663356, "alt": current_height}
    commandList = deque()
    commandList.append({"argType": "Fire", "lat": 33.9327418, "lon":  -117.6301938, "alt": current_height})
    commandList.append({"argType": "Evac", "lat": 33.9326391, "lon":  -117.6305475, "alt": current_height})

    while(len(commandList)>0):
        print("Running Mission")
        #check for command message, using test command for now
        #command = commandList.popleft()
        command = commandList[0]
        #command = commandList[1]
        # Parse command received
        if (command["argType"] == "Evac"):
            print("Evacing")
            drone.flyToCords(lat = command["lat"],lon = command["lon"], alt = command["alt"])
            # Call Winch Servo, start it up state
            evac_servo.step(EVAC_steps, True)   # release the winch, CCW
            time.sleep(PAYLOAD_WAIT)                 # wait for payload
            #for(int i = 0; i < 10000000; i++)
            evac_servo.step(EVAC_steps, False)         # return the winch, CW
        if (command["argType"] == "Fire"):
            print("Firing")
            drone.flyToCords(command["lat"], command["lon"], command["alt"])
            # Identify and Extinguish Fire

            fire_loc = fire_detector.red_detection()
            # # Wait for object to be detected
            #while box == None:
            #    box = fire_detector.red_detection()
            #drone.vehicle.mode = VehicleMode("LAND")
            print("Fire Location:")
            print(fire_loc)
            print("Extinguising")
            # Call Fire Servo, starts in relaxed state
            #fire_servo.step(FIRE_steps, True)   # squeeze fire extinguisher
            #fire_servo.step(FIRE_steps1, True)   # squeeze fire extinguisher
            #k = 0
            #while(k < 10):
                #time.sleep(0.01)
                #fire_servo.step(FIRE_steps2, True)   # squeeze fire extinguisher
            #time.sleep(FIRE_WAIT)                  # 7-15 seconds for exhuast
            #for(int i = 0; i < 10000000; i++)
            fire_servo.step(FIRE_steps, False)     # relax fire extinguisher

            #drone.armVehicle()
            #drone.takeoff(TAKEOFF_HEIGHT)
        # GCS is Always Updating
        print("Returning Home")
        drone.goHome()
        #ug.top()
        print("Done")
        while(1):
            k=0

    #Land Home / "Return to Launch &/or Home"
    #drone.goHome()
    #Stop GCS Update
    #ug.stop()

if __name__ == "__main__":
    main()
