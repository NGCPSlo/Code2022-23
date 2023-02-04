import json
from paho.mqtt import client as mqtt_client
import paho.mqtt
import constants


# Callback function to be called whenever the MEA receives a message from GCS
def on_message(client:mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
  dataString: str = msg.payload.decode()
  print(dataString)
  jsonMsg = json.loads(dataString)
  

  x = jsonMsg.get("search_area")
  y = jsonMsg.get("home_coordinates")
  z = jsonMsg.get("drop_coordinates")
    
  #search_area array with 3 objects holding lng and lat
  if x != None:
    search_lat_0 = x[0]["lat"]
    search_long_0 = x[0]["lng"]
    search_lat_1 = x[1]["lat"]
    search_long_1 = x[1]["lng"]
    search_lat_2 = x[2]["lat"]
    search_long_2 = x[2]["lng"]   
  
  
  
  #home_coordinates
  #assuming "4" is vehicle: MEDEVAC
  elif y != None:
    home_lat = y["2"]["lat"]
    home_long = y["2"]["lng"]
  
  
  #drop_coordinates
  elif z != None:
    drop_lat = z["lat"]
    drop_long = z["lng"]
  

def on_connect(client: mqtt_client.Client, userdata, flags: dict[str, int], rc: int):
  if(rc == 0):
    print("Connected to GCS successfully")
  elif(rc == 1):
    print("Connection refused - incorrect protocol version")
  elif(rc == 2):
    print("Connection refused - invalid client identifier")
  elif(rc == 3):
    print("Connection refused - server unavailable")
  elif(rc == 4):
    print("Connection refused - bad username or password")
  elif(rc == 5):
    print("Connection refused - not authorised")
  else:
    print("rc value incorrect, something went wrong")

class GCSClient:
  # Initializes a GCS Client object, set the topic to be MEA so GCS can target messages for us
  def __init__(self, broker: str = constants.broker, \
                     port: int = constants.port, \
                     topic: str = constants.topic, \
                    #  username: str = constants.username, \
                    #  password: str = constants.password, \
                     clientId: str = None) -> None:
    print("Initializing Client")
    self.topic = topic
    self.client = mqtt_client.Client("user")
    self.client.on_connect = on_connect
    self.client.on_message = on_message
    # self.client.username_pw_set(username, password)
    self.client.connect(broker, port)

   
  def subscribe(self):
    self.client.subscribe(self.topic)
    self.client.loop_start()
  
  # Publishes a message to the MQTT service
  def send(self, message:str, timeout:int = None):
    msgInfo: mqtt_client.MQTTMessageInfo = self.client.publish(self.topic, message, qos = 2)
    msgInfo.wait_for_publish(timeout)


  # def on_message( client, userdata, message):
  #   #checking message sent to client
  #     print("message received " ,str(message.payload.decode("utf-8")))
  #     print("message topic=",message.topic)
  #     print("message qos=",message.qos)
  #     print("message retain flag=",message.retain)
  

if __name__ == '__main__':
  backend = GCSClient()
  backend.subscribe()
  while(True):
    pass
