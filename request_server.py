import json
import string
import time
import constants
import requests
import argparse
import random
import socket
# from flask import Flask, jsonify
# #send


# #to do
# ip_address = 'localhost'
# port = 3000
# def post(request_data: requests):
#     """
#     Sends status information to GCS
#     type_msg: type of message sent to GCS
#     status: quantitative value like coordinates
#     """
#     requests.post(f"http://{ip_address}:{port}/get-json", request_data) #stores data inside get-json
#     time.sleep(0.5)

# app = Flask(__name__)


# @app.route('/get-json', methods=['GET'])
# def send_cords(data: str):
#     """
#     sends coordinate information to get-json
#     """
#     search_area = requests.get(f"http://{ip_address}:{port}/search_area")
#     home_cords = requests.get(f"http://{ip_address}:{port}/home_coordinates")
#     evac_cords = requests.get(f"http://{ip_address}:{port}/evacuation_coordinates")
#     geofence = requests.get(f"http://{ip_address}:{port}/geofence")
#     if data == "search":
#         post(search_area)
#     if data == "home":
#         post(home_cords)
#     if data == "evac":
#         post(evac_cords)
#     if data == "geo":
#         post(geofence)
        
#     # else:
#     #     send_cords(data) #store data recieved from client onto database



def main():
    host = socket.gethostname()
    port = 3000  # initiate port no above 1024
    server_socket = socket.socket()  # get instance

    server_socket.bind((host, port))  # bind host address and port together

    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection
    
    print("Connection from: " + str(address))
    message = input(" -> ")  # take input
    while message.lower().strip() != 'bye':
        conn.send(message.encode())  # send message
        message = input(" -> ")  # again take input
    conn.close()  # close the connection

if __name__ == '__main__':
    main()