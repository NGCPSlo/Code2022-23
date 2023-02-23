#simulator device 1 for mqtt message publishing
import paho.mqtt.client as paho
import time
import random
import json
import keyboard

#hostname
broker="localhost"
#port
port=1883
def on_publish(client,userdata,result):
    print("Data Published")
    pass

client= paho.Client("admin")
client.on_publish = on_publish
client.connect(broker,port)

message = ""
#for i in range(20):
#    d=random.randint(1,5)                
#    #telemetry to send 
#    message="Device 1 : Data " + str(i)


command_geo = '{"geofence":[{"coordinates":[{"lat":0.0,"lng":0.0},{"lat":0.0,"lng":0.0},{"lat":0.0,"lng":0.0}],"keep_in":true},{"coordinates":[{"lat":0.0,"lng":0.0},{"lat":0.0,"lng":0.0},{"lat":0.0,"lng":0.0}],"keep_in":false}]}'
command_search = '{"search_area":[{"lng":0.0,"lat":0.0},{"lat":0.0,"lng":0.0},{"lat":0.0,"lng":0.0}]}'
command_home = '{"home_coordinates":{"2":{"vehicle":"MEA","lat":33.9,"lng":-117.6}}}'
command_drop = '{"drop_coordinates":{"lat":33.9,"lng":-117}}'
command_evac = '{"evacuation_coordinates":{"lat":33.9,"lng":-117.6}}'

while(1):
    if (keyboard.read_key() == "g"):
        message = command_geo
    elif (keyboard.read_key() == "s"):
        message = command_search
    elif (keyboard.read_key() == "h"):
        message = command_home
    elif (keyboard.read_key() == "d"):
        message = command_drop
    elif (keyboard.read_key() == "e"):
        message = command_evac
    else:
        message = ""



#time.sleep(d)
#publish message
    if(len(message) > 0):
        ret = client.publish("/data",message)
print("Stopped...")