import json
import string
import time
import requests
import argparse
import random
import socket
from flask import Flask, jsonify

#CRUD

class Coordinates:
    def __init__(self):
        self.type = None
        self.lng1 = None
        self.lat1 = None
        self.lng2 = None
        self.lat2 = None
        self.lng3 = None
        self.lat3 = None
    
    def __eq__(self, other):
        if isinstance(other, Coordinates):
            return self.type == other.type and \
                    self.lng1 == other.lng1 and \
                    self.lat1 == other.lat1 and \
                    self.lng2 == other.lng2 and \
                    self.lat2 == other.lat2 and \
                    self.lat3 == other.lat3 and \
                    self.lng3 == other.lng3

    def __str__(self):
        if (self.type == "home" or self.type == "evac"):
            return f'{self.type}: lat1: {self.lat1}, lng1: {self.lng1}'

        else:
            return f'{self.type}: lat1: {self.lat1}, lng1: {self.lng1}, lat2: {self.lat2}, lng2: {self.lng2}, lat3: {self.lat3}, lng3: {self.lng3}'
                    
    def __repr__(self):
        """
        prints out the Coordinate structure defined in init
        """
        lng1_repr = self.format_value(self.lng1)
        lat1_repr = self.format_value(self.lat1)
        lng2_repr = self.format_value(self.lng2)
        lat2_repr = self.format_value(self.lat2)
        lng3_repr = self.format_value(self.lng3)
        lat3_repr = self.format_value(self.lat3)
        return f'Coordinates(\'{self.type}\', {lat1_repr}, {lng1_repr}, {lat2_repr}, {lng2_repr}, {lat3_repr}, {lng3_repr})'

    def format_value(self, value):
        """
        used for repr
        """
        if value is None:
            return None
        elif value >= 0:
            return str(value)
        else:
            return f'-{abs(value)}'

    def get_search(self, ip_address, port: int):
        data = requests.get(f"http://{ip_address}:{port}/search_area").json()
        search_lat_0 = data[0]["lat"]
        search_long_0 = data[0]["lng"]
        search_lat_1 = data[1]["lat"]
        search_long_1 = data[1]["lng"]
        search_lat_2 = data[2]["lat"]
        search_long_2 = data[2]["lng"]    
    
        self.type = "search"
        self.lng1 = search_long_0
        self.lat1 = search_lat_0
        self.lng2 = search_long_1
        self.lat2 = search_lat_1
        self.lng3 = search_long_2
        self.lat3 = search_lat_2
        return self

    def get_fire(self, ip_address, port: int):
        data = requests.get(f"http://{ip_address}:{port}/fire_location").json()
        search_lat_0 = data[0]["lat"]
        search_long_0 = data[0]["lng"]
        search_lat_1 = data[1]["lat"]
        search_long_1 = data[1]["lng"]
        search_lat_2 = data[2]["lat"]
        search_long_2 = data[2]["lng"]    
    
        self.type = "fire"
        self.lng1 = search_long_0
        self.lat1 = search_lat_0
        self.lng2 = search_long_1
        self.lat2 = search_lat_1
        self.lng3 = search_long_2
        self.lat3 = search_lat_2
        return self

    def get_evac(self, ip_address, port: int):
        data =  requests.get(f"http://{ip_address}:{port}/evacuation_coordinates").json()
        drop_lat = data["lat"]
        drop_long = data["lng"]    
    
        self.type = "evac"
        self.lng1 = drop_long
        self.lat1 = drop_lat
        return self

    def get_home(self, ip_address, port: int):
        data =  requests.get(f"http://{ip_address}:{port}/home_coordinates").json()
        home_lat = data['2']["lat"]
        home_long = data['2']["lng"]    
    
        self.type = "home"
        self.lat1 = home_lat
        self.lng1 = home_long
        return self

    def clear(self):
        """
        turns self into None, used for get_cords
        """
        self.type = None
        self.lng1 = None
        self.lat1 = None
        self.lng2 = None
        self.lat2 = None
        self.lng3 = None
        self.lat3 = None
        return self

    def set_cords(self, type, lat1, lng1, lat2, lng2, lat3, lng3):
        """
        sets the cords in self to a given value
        """
        self.type = type
        self.lng1 = lng1
        self.lat1 = lat1
        self.lng2 = lng2
        self.lat2 = lat2
        self.lng3 = lng3
        self.lat3 = lat3
        return self

    def get_cords(self, ip_address, port: int):
        """
        Regularly requests coordinates from GCS database,a match exists if there's a difference in coordinates
        
        the difference in coordinates(stored in this function and the one inside the database) occurs when GCS
        writes to the database at the specified location
        """
        search_store = Coordinates()
        fire_store = Coordinates()
        home_store = Coordinates()

        while True:
            #print("inside get_cords while loop")
            self.get_search(ip_address, port)
            #print("self:", repr(self))
            if search_store.type is None:
                search_store.set_cords(self.type, self.lat1, self.lng1, self.lat2, self.lng2, self.lat3, self.lng3)
            elif not (search_store == self):
                return search_store
            #print("self:", repr(self))
            #print("search:", repr(search_store))



            self.clear()
            self.get_fire(ip_address, port)
            #print("self:", repr(self))
            if fire_store.type is None:
                fire_store.set_cords(self.type, self.lat1, self.lng1, self.lat2, self.lng2, self.lat3, self.lng3)
            elif not (fire_store == self):
                return fire_store
            #print("self:", repr(self))
            #print("fire:", repr(fire_store))
                        
            self.clear()
            self.get_home(ip_address, port)
            #print("self:", repr(self))
            if home_store.type is None:
                home_store.set_cords(self.type, self.lat1, self.lng1, None, None, None, None)
            elif not (home_store == self):
                return home_store
            #print("self:", repr(self))
            #print("home:", repr(home_store))
                                    
            self.clear()
            time.sleep(10)  # Pause regular retrieval


    def post_cords(self, ip_address: str, msg_type: str, port: int):
        """
        posts coordinate information to GCS in the given area
        example:
            coordinates = [
                {"lng": 12, "lat": 14},
                {"lng": 1, "lat": 3},
                {"lng": 5, "lat": 17}
            ]
        """
        # POST updated search area coords onto the database. 
        #sends information to GCS 
        cords = self.cords_conversion()
        try:
            requests.post(f"http://{ip_address}:{port}/{msg_type}", json=cords)
        except requests.exceptions.JSONDecodeError:
            print("JSONDecodeError: cannot return response body at this time")
        # Cool down period of 0.5 seconds
        time.sleep(0.5)
    
    def cords_conversion(self):
        """
        Converts the class into an array and converts it
        used for post_cords
        """
        cords = [
            {"lat": self.lat1, "lng": self.lng1},
            {"lat": self.lat2, "lng": self.lng2},
            { "lat": self.lat3, "lng": self.lng3}
        ]        
        return cords
        
        # if self.type == "search":
        #     cords = [
        #         {"lng": self.lng1 , "lat": self.lat1},
        #         {"lng": self.lng2, "lat": self.lat2},
        #         {"lng": self.lng3, "lat": self.lat3},
        #     ]
        #     return cords
        # elif self.type == "current":
        #     cords = [
                
        #     ]