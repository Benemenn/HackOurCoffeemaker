import paho.mqtt.client as mqtt


class BrokerConfig():
    mqtt_broker = "192.168.178.21"
    mqtt_port = 1883
    mqtt_keepalive = 60
    mqtt_topic_energyData = "bipfinnland/monitoring9/data"

broker = BrokerConfig()

# Define the callback function for when a message is received
def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}' with QoS {message.qos}")

# Define the callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribe to the topic here
    client.subscribe(broker.mqtt_topic_energyData)

# Create an MQTT client instance
client = mqtt.Client(protocol=mqtt.MQTTv311)

# Assign the on_connect and on_message callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker.mqtt_broker, broker.mqtt_port, broker.mqtt_keepalive)  # Use the broker address and port number

if input("Start?") == "start":
    client.loop_start()

