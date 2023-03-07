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
    response_object = {'status': 'success'}
    if request.method == 'POST':
        search_area_coordinates = request.json['post_current']
        lat = search_area_coordinates['lat']
        lng = search_area_coordinates['lng']
        
        print("current_location")
        print("lat_0", lat, "long_0", lng)
        
        #print(search_area_coordinates)
        return ""
        #with open("db.json", 'w') as jsonfile:
            #json.dump(search_area_coordinates, jsonfile)
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


def main():
    app.run(debug = True)

if __name__ == '__main__':
    main()