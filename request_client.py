import json
import string
import time
import constants
import requests
import argparse
import random
import socket
from flask import Flask, jsonify

ip_address = 'localhost'  # The server's hostname or IP address
PORT = 3000         # The port used by the server

#status: 
#want to recieve data from GCS at any time, create a flask server on client
#requesting content from GCS
#dealing with post request
#sending data back
#if value changes, then parse then


#code to write
#write client to request data from server periodically
# sending information to server(not working), updating the database(?)


# def post(gcs_send: string, type_msg: string, status: string):
#     """
#     Sends status information to GCS(server)
#     type_msg: type of message sent to GCS(server)
#     status: quantitative value like coordinates
#     """
#     requests.post(gcs_send, data = {type_msg , status})
    

# def request(GCS_msg: string):
#     """
#     recieves json information from GCS(server)
#     """
    
#     response = requests.get(GCS_msg)
#     if response.status_code == 200:
#         on_message(response)
#     elif response.status_code == 404:
#         print('Not Found')

def connect(ip_address: str = '127.0.0.1'):
    """
    connects to GCS(server)
    """
    if ip_address == None:
        ip_address = '127.0.0.1'
    on_message(ip_address)
    
    
def json_message(direction):
    local_ip = socket.gethostbyname(socket.gethostname())
    data = {
        'sender': local_ip,
        'instruction': direction
    }

    json_data = json.dumps(data, sort_keys=False, indent=2)
    print("data %s" % json_data)

    send_message(json_data + ";")

    return json_data


def send_message(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(data.encode())
        data = s.recv(1024)

    print('Received', repr(data))    
    

def client_program(ip_address, port):
    host = socket.gethostname()  # as both code is running on same pc
    port = 3000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = client_socket.recv(1024).decode()
        if not data:
            # if data is not received break
            break
        on_message_mod(data, port)

    client_socket.close()  # close the connection    


def on_message_mod(requested: str, port: int):
    """
    Parse message recieved from GCS and retrieves data from database
    """
    
    # search_area array with 3 objects holding lng and lat
    if (requested == "search"):
        data = requests.get(f"http://{ip_address}:{port}/search_area").json()
        search_lat_0 = data[0]["lat"]
        search_long_0 = data[0]["lng"]
        search_lat_1 = data[1]["lat"]
        search_long_1 = data[1]["lng"]
        search_lat_2 = data[2]["lat"]
        search_long_2 = data[2]["lng"]
        
        print("search_coordinates")
        print("lat_0", search_lat_0, "long_0", search_long_0)
        print("lat_1", search_lat_1, "long_1", search_long_1)
        print("lat_2", search_lat_2, "long_2", search_long_2)
        print(" ")
        
    # home_coordinates
    # assuming "4" is vehicle: MEDEVAC
    elif (requested == "home"):
        data = requests.get(f"http://{ip_address}:{port}/home_coordinates").json()
        home_lat = data['2']["lat"]
        home_long = data['2']["lng"]
        print("home_coordinates")
        print("home_lat", home_lat, "home_long", home_long)
        print(" ")
    
    # drop_coordinates
    elif (requested == "evac"):
        data =  requests.get(f"http://{ip_address}:{port}/evacuation_coordinates").json()
        drop_lat = data["lat"]
        drop_long = data["lng"]
        print("evac")
        print("drop_lat", drop_lat, "drop_long", drop_long)
        print(" ")

    elif (requested == "geo"):
        data = requests.get(f"http://{ip_address}:{port}/geofence").json()
        # keep_in: true
        geo_lat_0_t = data[0]["coordinates"][0]["lat"]
        geo_lng_0_t = data[0]["coordinates"][0]["lng"]
        geo_lat_1_t = data[0]["coordinates"][1]["lat"]
        geo_lng_1_t = data[0]["coordinates"][1]["lng"]
        geo_lat_2_t = data[0]["coordinates"][2]["lat"]
        geo_lng_2_t = data[0]["coordinates"][2]["lng"]

        print("geo")
        print("lat_0", geo_lat_0_t, "long_0", geo_lng_0_t)
        print("lat_1", geo_lat_1_t, "long_1", geo_lng_1_t)
        print("lat_2", geo_lat_2_t, "long_2", geo_lng_2_t)

        # keep_in: false
        geo_lat_0_f = data[1]["coordinates"][0]["lat"]
        geo_lng_0_f = data[1]["coordinates"][0]["lng"]
        geo_lat_1_f = data[1]["coordinates"][1]["lat"]
        geo_lng_1_f = data[1]["coordinates"][1]["lng"]
        geo_lat_2_f = data[1]["coordinates"][2]["lat"]
        geo_lng_2_f = data[1]["coordinates"][2]["lng"]

        print("lat_0", geo_lat_0_f, "long_0", geo_lng_0_f)
        print("lat_1", geo_lat_1_f, "long_1", geo_lng_1_f)
        print("lat_2", geo_lat_2_f, "long_2", geo_lng_2_f)
        print(" ")
    
    else:
        print("either send was requested or error")


# def send_cords(ip_address: str, msg_type: str, cords: str, port: int):
#     #sends coordinate information to GCS
#     request_body = {
#         msg_type: [
#             {
#                 "lat": cords[0][0],
#                 "lng": cords[0][1]
#             },
#             {
#                 "lat": cords[1][0],
#                 "lng":cords[1][1]
#             },
#             {
#                 "lat": cords[2][0],
#                 "lng": cords[2][1]
#             }
#         ]
#     }    
#     # POST updated search area coords onto the database. 
#     #sends information to GCS 
#     try:
#         #requests.post(f"http://{ip_address}:{port}/post{msg_type}", json=request_body)
#         requests.post(f"http://{ip_address}:{port}/{msg_type}", json=request_body)
#     except requests.exceptions.JSONDecodeError:
#         print("JSONDecodeError: cannot return response body at this time")
#     # Cool down period of 0.5 seconds
#     time.sleep(0.5)


def send_cords(ip_address: str, msg_type: str, cords: str, port: int):
    #sends coordinate information to GCS
    request_body = {
        msg_type: 
            {
                "lat": cords[0][0],
                "lng": cords[0][1]
            }
    }    
    # POST updated search area coords onto the database. 
    #sends information to GCS 
    try:
        #requests.post(f"http://{ip_address}:{port}/post{msg_type}", json=request_body)
        requests.post(f"http://{ip_address}:{port}/{msg_type}", json=request_body)
    except requests.exceptions.JSONDecodeError:
        print("JSONDecodeError: cannot return response body at this time")
    # Cool down period of 0.5 seconds
    time.sleep(0.5)
















def main():
    cords = [[25, 10], [15,4], [11, 12]] #test current locations
    ip_address = 'localhost'
    port = 5000
    # on_message_mod("geo", port)
    # on_message_mod("search", port)
    # on_message_mod("evac", port)
    # on_message_mod("home", port)
    #send_cords(ip_address, "postSearchArea", cords, port)
    send_cords(ip_address, "post_current", cords, port)
if __name__ == '__main__':
    main()
    # while (True):
    #     pass