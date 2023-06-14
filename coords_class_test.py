import json
import string
import time
import requests
import argparse
import random
import socket
import time

from flask import Flask, jsonify
 
from coords_class import Coordinates


#Given by GCS prior to the Demo
ip_address = 'localhost'  # The server's hostname or IP address
PORT = 5000         # The port used by the server




def main():
    #print("hello")
    get_test()


def post_cords():
    """
    tests functionality of the post cord function
    """
    post_cords = Coordinates()
    post_cords.set_cords("post_cords", 1, 2, 3, 4, 5, 6)
    # coordinates = [
    #     {"lat": 1, "lng": 14},
    #     {"lat": 11, "lng": 3},
    #     {"lat": 9, "lng": 17}
    # ]
    
    post_cords.post_cords(ip_address, "post_current", PORT)


def get_test():
    """
    tests the functionality of the get_cords function
    """
    retrv_cords = Coordinates().get_cords(ip_address, PORT)
    
    print(repr(retrv_cords))
    print(str(retrv_cords))


def sget_test():
    """
    tests the functionality of the seperate get functions
    
    """
    scords = Coordinates()
    hcords = Coordinates()
    fcords = Coordinates()
    
    search = scords.get_search(ip_address, PORT)
    print(repr(search))
    print(str(search))
    
    home = hcords.get_home(ip_address, PORT)
    print(repr(home))
    print(str(home))
    
    fire = fcords.get_fire(ip_address, PORT)
    print(repr(fire))
    print(str(fire))    




if __name__ == '__main__':
    main()    