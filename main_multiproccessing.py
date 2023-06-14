from multiprocessing import Lock, Process, Queue, current_process
import time
import queue # imported for using queue.Empty exception
import signal
from coords_class import Coordinates
import random

#The integration code was meant to be run in a MULTI-PROCESSING way


#Given by GCS prior to the Demo
ip_address = 'localhost'  # The server's hostname or IP address
PORT = 5000         # The port used by the server

def sending():
    """
    regularily sends coordinates to GCS
    """
    while(True):
        time.sleep(2)
        send_cords = retrieve_pixhawk_cords()
        send_cords.post_cords(ip_address, "post_current", PORT) #sends coordinates
        print("Done sending to pixhawk")

def retrieve_pixhawk_cords():
    """
    boiler plate code used for 
    retrieving the coordinates from the pixhawk flight controller
    and returning coordinates in a class structure
    
    insert code for retrieving cords from pixhawk flight controller here!
    """
    print("retrieve pixhawk coordinates")
    
    #hard-coded values
    lat_0 = random.randint(0, 20)
    lng_0 = random.randint(0, 20)
    lat_1 = random.randint(0, 20)
    lng_1 = random.randint(0, 20)
    lat_2 = random.randint(0, 20)
    lng_2 = random.randint(0, 20)   
    
    pixhawk_cords = Coordinates()
    pixhawk_cords.set_cords("post_cords", lat_0, lng_0, lat_1, lng_1, lat_2, lng_2)    
    
    return pixhawk_cords

def recieving():
    """
    testing purposes only
    boilerplate code for retrieving coordinates from GCS
    """
    recv_cords = Coordinates()
    while(True):
        print("running recieving")
        recv_cords = recv_cords.get_cords(ip_address, PORT)
        AutoFlight(recv_cords)

def winch_motor(coordinates):
    if (coordinates.type == "fire"):
        print("winch motor for extinguisher activated")
    elif (coordinates.type == "search"):
        print("winch motor for retrieval activated")

def AutoFlight(coordinates):
    """
    testing purposes
    boilerplate code for sending info to pixhawk and commanding other processes
    """
    
    if (coordinates.type == "search"):
        rescue_mission(coordinates)
        winch_motor(coordinates)

    elif (coordinates.type == "fire"):
        fire_detection(coordinates)
        winch_motor(coordinates)
        
    elif (coordinates.type == "home"):
        fly_home(coordinates)

def send_pixhawk(coordinates):
    """
    boiler plate code used for 
    sending flight coordinates to the pixhawk flight controller

    insert code for sending cords to pixhawk flight controller here!
    """

    print("sending cords to pixhawk flight controller for type:", coordinates.type)


def winch_motor(coordinates):
    if (coordinates.type == "fire"):
        print("winch motor for extinguisher activated")
    elif (coordinates.type == "search"):
        print("winch motor for retrieval activated")

def rescue_mission(coordinates):
    """
    rescue_mission
    """

    print("rescue mission activated")
    print(str(coordinates))
    send_pixhawk((coordinates))
    
def fire_detection(coordinates):
    """
    fire detection function
    call fire detection library here
    """
    print("fire rescue operation activated:")
    print(str(coordinates))
    send_pixhawk((coordinates))

def fly_home(coordinates):
    """
    sends the coordinates to the pixhawk to fly home
    """
    print("flying home")
    print(str(coordinates))
    send_pixhawk((coordinates))


def main():
    processes = []    
    p = Process(target = sending, args=()) #creating sending process
    processes.append(p)
    p.start()

    p = Process(target = recieving, args = ()) #creating recieving process
    processes.append(p)
    p.start()

    for p in processes:
        p.join() 
    

if __name__ == '__main__':
    main()