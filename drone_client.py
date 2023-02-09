
import math
import time

import collections
try:
    from collections import abc
    collections.MutableMapping = abc.MutableMapping
except:
    pass

from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative

class DroneClient:
    def __init__(self, connectionStr: str =  "/dev/ttyS0") -> None:
        
        self.connectionStr = connectionStr
        self.vehicle = None
        
    def connect(self, baud: int = 57600):
        '''
        Connects to vehicle and blocks until it is ready
        '''
        print("Connecting to vehicle on: %s" % (self.connectionStr,))
        self.vehicle = connect(self.connectionStr, wait_ready=False,)
        self.vehicle.wait_ready(True, raise_exception=False)
    
    def armVehicle(self):
        """
        Ensures vehicle is ready to arm and arms it.
        """

        if self.vehicle == None:
            raise Exception("Vehicle not connected")
        
        # Waits until drone is armable
        while not self.vehicle.is_armable:
            print(" Waiting until armable...")
            time.sleep(1)

        # Sets the drone mode to guided, blocks until complete
        print("Arming the vehicle")
        self.vehicle.mode =  VehicleMode("GUIDED")
        while self.vehicle.mode.name != "GUIDED":
            time.sleep(1)
        
        # Set vehicle to armed and blocks until it is

        self.vehicle.armed = True
        while not self.vehicle.armed:
            print(" Waiting for arming...")
            time.sleep(1)

    def takeoff(self,heightInM):
        self.vehicle.simple_takeoff(alt=heightInM)
        # Delay until takeoff height is reached
        while self.vehicle.mode.name=="GUIDED":
            print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
            # Within 5% of target altitude or within 1m 
            if self.vehicle.location.global_relative_frame.alt>=heightInM*0.95 or\
             abs(self.vehicle.location.global_relative_frame.alt-heightInM) < 1:
                print("Reached target altitude")
                break
            time.sleep(1)
    
    
    #* get_location_metres - Get LocationGlobal (decimal degrees) at distance (m) North & East of a given LocationGlobal.
    def get_location_metres(self, original_location, dNorth, dEast):
        """
        Returns a LocationGlobal object containing the latitude/longitude `dNorth` and `dEast` metres from the 
        specified `original_location`. The returned LocationGlobal has the same `alt` value
        as `original_location`.

        The function is useful when you want to move the vehicle around specifying locations relative to 
        the current vehicle position.

        The algorithm is relatively accurate over small distances (10m within 1km) except close to the poles.

        For more information see:
        http://gis.stackexchange.com/questions/2951/algorithm-for-offsetting-a-latitude-longitude-by-some-amount-of-meters
        """
        earth_radius = 6378137.0 #Radius of "spherical" earth
        #Coordinate offsets in radians
        dLat = dNorth/earth_radius
        dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

        #New position in decimal degrees
        newlat = original_location.lat + (dLat * 180/math.pi)
        newlon = original_location.lon + (dLon * 180/math.pi)
        if type(original_location) is LocationGlobal:
            targetlocation=LocationGlobal(newlat, newlon,original_location.alt)
        elif type(original_location) is LocationGlobalRelative:
            targetlocation=LocationGlobalRelative(newlat, newlon,original_location.alt)
        else:
            raise Exception("Invalid Location object passed")
            
        return targetlocation

    #* get_distance_metres - Get the distance between two LocationGlobal objects in metres
    def get_distance_metres(self, aLocation1, aLocation2):
        """
        Returns the ground distance in metres between two LocationGlobal objects.

        This method is an approximation, and will not be accurate over large distances and close to the 
        earth's poles. It comes from the ArduPilot test code: 
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """
        dlat = aLocation2.lat - aLocation1.lat
        dlong = aLocation2.lon - aLocation1.lon
        return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

    #* get_bearing - Get the bearing in degrees to a LocationGlobal
    def get_bearing(self, aLocation1, aLocation2):
        """
        Returns the bearing between the two LocationGlobal objects passed as parameters.

        This method is an approximation, and may not be accurate over large distances and close to the 
        earth's poles. It comes from the ArduPilot test code: 
        https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
        """	
        off_x = aLocation2.lon - aLocation1.lon
        off_y = aLocation2.lat - aLocation1.lat
        bearing = 90.00 + math.atan2(-off_y, off_x) * 57.2957795
        if bearing < 0:
            bearing += 360.00
        return bearing

    def flyToMeters(self, dNorth, dEast, gotoFunction = None):
        """
        Takes in Cartesian coordinates in meters as a target to fly to. 
        Then flies the vehicle to the target location, stopping once the target has been reached.
        """
        currentLocation=self.vehicle.location.global_relative_frame
        targetLocation=self.get_location_metres(currentLocation, dNorth, dEast)
        targetDistance=self.get_distance_metres(currentLocation, targetLocation)
        if(gotoFunction == None):
            gotoFunction = self.vehicle.simple_goto
        gotoFunction(targetLocation)

        while self.vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
            remainingDistance=self.get_distance_metres(self.vehicle.location.global_frame, targetLocation)
            print("Distance to target: ", remainingDistance)
            if remainingDistance<=max(targetDistance*0.01, 1): #Just below target, in case of undershoot.
                print("Reached target")
                break
            time.sleep(1)

    def printVehicleState(self):
        # Prints some vehicle attributes (state)
        vehicle = self.vehicle
        print("Get some vehicle attribute values:")
        print(" GPS: %s" % vehicle.gps_0)
        print(" Battery: %s" % vehicle.battery)
        print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
        print(" Is Armable?: %s" % vehicle.is_armable)
        print(" System status: %s" % vehicle.system_status.state)
        print(" Mode: %s" % vehicle.mode.name)    # settable
        print(" Location: %s" % vehicle.location.global_frame)  

    def goHome(self):
        self.vehicle.mode("RTL")

    def flyToCords(self, lat:float, lon: float, alt: float = None):
        '''
        Sets vehicle target destination to a set of coordinates and blocks until destination reached
        '''
        startLocation=self.vehicle.location.global_relative_frame
        targetLocation = LocationGlobalRelative(lat, lon, alt)
        self.vehicle.simple_goto(targetLocation)

        targetDistance=self.get_distance_metres(startLocation, targetLocation)

        while self.vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
            remainingDistance=self.get_distance_metres(self.vehicle.location.global_frame, targetLocation)
            print("Distance to target: ", remainingDistance)
            #Block until 1% of target distance is reached or within 1m
            if remainingDistance<=max(targetDistance*0.01, 1): 
                print("Reached target")
                break
            time.sleep(1)


if __name__ == '__main__':
  drone = DroneClient()
  drone.connect()
  drone.armVehicle()
  drone.takeoff(20)


  pass
