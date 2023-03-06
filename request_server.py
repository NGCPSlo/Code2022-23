import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/geofence', methods=['GET'])
def getGeofence():
    with open("db.json") as jsonfile:
        datavalue = json.load(jsonfile)
        return json.dumps(datavalue.get("geofence", "")) #sends data in string format

@app.route('/search_area', methods=['GET'])
def getSearch():
    with open("db.json") as jsonfile:
        datavalue = json.load(jsonfile)
        return json.dumps(datavalue.get("search_area", ""))

@app.route('/postSearchArea', methods=['POST'])
def post_search_area():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        search_area_coordinates = request.json
        with open("db.json", 'w') as jsonfile:
            json.dump(search_area_coordinates, jsonfile)
            #jsonfile.insert(search_area_coordinates)
    # return jsonify(response_object)

@app.route('/home_coordinates', methods=['GET'])
def getHome():
    with open("db.json") as jsonfile:
        datavalue = json.load(jsonfile)
        return json.dumps(datavalue.get("home_coordinates", ""))

@app.route('/evacuation_coordinates', methods=['GET'])
def getEvac():
    with open("db.json") as jsonfile:
        datavalue = json.load(jsonfile)
        return json.dumps(datavalue.get("evacuation_coordinates", ""))



# def connect():
#     host = socket.gethostname()
#     port = 3000  # initiate port no above 1024
#     server_socket = socket.socket()  # get instance

#     server_socket.bind((host, port))  # bind host address and port together

#     server_socket.listen(2)
#     conn, address = server_socket.accept()  # accept new connection
    
#     print("Connection from: " + str(address))
#     message = input(" -> ")  # take input
#     while message.lower().strip() != 'bye':
#         conn.send(message.encode())  # send message
#         message = input(" -> ")  # again take input
#     conn.close()  # close the connection



def main():
    app.run(debug = True)

if __name__ == '__main__':
    main()