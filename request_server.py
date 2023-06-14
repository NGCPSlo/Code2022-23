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

@app.route('/fire_location', methods=['GET'])
def getFire():
    with open("db.json") as jsonfile:
        datavalue = json.load(jsonfile)
        return json.dumps(datavalue.get("fire_location", ""))



# @app.route('/postSearchArea', methods=['POST'])
# def post_search_area():
#     response_object = {'status': 'success'}
#     if request.method == 'POST':
#         search_area_coordinates = request.json
#         print(search_area_coordinates)
#         return
#         #with open("db.json", 'w') as jsonfile:
#             #json.dump(search_area_coordinates, jsonfile)
#             #jsonfile.insert(search_area_coordinates)
#     # return jsonify(response_object)
    
    
@app.route('/post_current', methods=['POST'])
def post_current():
    
    # Read the existing contents of the db.json file
    with open('db.json', 'r') as file:
        data = json.load(file)
    
    # Get the new coordinate information from the request
    coordinates = request.json
    
    # Update the post_current section with the new coordinate information
    data["post_current"] = coordinates
    
    # Write the updated data back to the db.json file
    with open('db.json', 'w') as file:
        json.dump(data, file, indent=2)
    return "success"

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


def main():
    app.run(debug = True)

if __name__ == '__main__':
    main()