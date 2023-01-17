print("Start simulator (SITL)")
connection_string = "udp:127.0.0.1:14551"
# Import DroneKit-Python
import math
import time
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative

# Connect to the Vehicle.
print("Connecting to vehicle on: %s" % (connection_string,))
vehicle = connect(connection_string, wait_ready=True)

"""
* get_location_metres - Get LocationGlobal (decimal degrees) at distance (m) North & East of a given LocationGlobal.
* get_distance_metres - Get the distance between two LocationGlobal objects in metres
* get_bearing - Get the bearing in degrees to a LocationGlobal
"""

def get_location_metres(original_location, dNorth, dEast):
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


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def get_bearing(aLocation1, aLocation2):
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

def goto(dNorth, dEast, gotoFunction=vehicle.simple_goto):
  currentLocation=vehicle.location.global_relative_frame
  targetLocation=get_location_metres(currentLocation, dNorth, dEast)
  targetDistance=get_distance_metres(currentLocation, targetLocation)
  gotoFunction(targetLocation)

  while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
      remainingDistance=get_distance_metres(vehicle.location.global_frame, targetLocation)
      print("Distance to target: ", remainingDistance)
      if remainingDistance<=max(targetDistance*0.01, 1): #Just below target, in case of undershoot.
          print("Reached target")
          break
      time.sleep(2)

# Get some vehicle attributes (state)
print("Get some vehicle attribute values:")
print(" GPS: %s" % vehicle.gps_0)
print(" Battery: %s" % vehicle.battery)
print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
print(" Is Armable?: %s" % vehicle.is_armable)
print(" System status: %s" % vehicle.system_status.state)
print(" Mode: %s" % vehicle.mode.name)    # settable


print(" Location: %s" % vehicle.location.global_frame)  

while not vehicle.is_armable:
  time.sleep(1)

print("Arming the vehicle")
vehicle.mode =  VehicleMode("GUIDED")
vehicle.armed = True
# Confirm vehicle armed before attempting to take off
while not vehicle.armed:
  print(" Waiting for arming...")
  time.sleep(1)


target_alt = vehicle.location.global_relative_frame.alt + 50
vehicle.simple_takeoff(alt=target_alt)

vehicle.parameters
print(" Location: %s" % vehicle.location.global_frame)  

while True:
  print(" Altitude: ", vehicle.location.global_relative_frame.alt)
  #Break and return from function just below target altitude.
  if vehicle.location.global_relative_frame.alt>=target_alt*0.95 or abs(vehicle.location.global_relative_frame.alt-target_alt) < 1:
      print("Reached target altitude")
      break
  time.sleep(1)

print("Let it vibe for 15 seconds")
time.sleep(15)
print("Flying to destination")
vehicle.mode = VehicleMode('GUIDED')
while vehicle.mode.name != "GUIDED":
  time.sleep(1)
goto(50, 35)
goto(-100, -10)
goto(20, 16)
goto(-5, 5)
print("Returning Home")
vehicle.mode = VehicleMode('RTL')

# Close vehicle object before exiting script
vehicle.close()

print("Completed")