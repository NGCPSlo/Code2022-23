from paho.mqtt import client as mqtt_client
import paho.mqtt
import constants


class GCSClient:
  # Initializes a GCS Client object, set the topic to be MEA so GCS can target messages for us
  def __init__(self, broker: str = constants.broker, \
                     port: int = constants.port, \
                     topic: str = constants.topic, \
                     username: str = constants.username, \
                     password: str = constants.password, \
                     clientId: str = None) -> None:
    
    self.topic = topic
    self.client = mqtt_client.Client(clientId)
    self.client.username_pw_set(username, password)
    self.client.connect(broker, port)
    self.client.on_connect = self.on_connect

  def on_connect(self, client: mqtt_client.Client, userdata, flags: dict[str, int], rc: int):
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
  
  # Callback function to be called whenever the MEA receives a message from GCS
  def on_message(self, client:mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
    dataString: str = msg.payload.decode()

    pass
  
  def subscribe(self):
    self.client.subscribe(self.topic)
    self.client.on_message = self.on_message
    self.client.loop_start()
  
  # Publishes a message to the MQTT service
  def send(self, message:str, timeout:int = None):
    msgInfo: mqtt_client.MQTTMessageInfo = self.client.publish(self.topic, message, qos = 2)
    msgInfo.wait_for_publish(timeout)

  

if __name__ == '__main__':
  backend = GCSClient()
  backend.subscribe()

  pass
