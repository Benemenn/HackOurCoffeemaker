import paho.mqtt.client as mqtt
import json
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime
import os
import threading
import time

# MQTT connection settings
MQTT_BROKER = "192.168.178.21"
MQTT_PORT = 1883
MQTT_TOPIC = "bipfinnland/monitoring9/data"

# Global variables to manage data collection
collecting_data = False
data_list = []
file_name = "coffee_machine_data.xlsx"

# Callback when the client receives a message from the server
def on_message(client, userdata, msg):
    global data_list, collecting_data
    
    if collecting_data:
        # Parse the JSON message
        message = json.loads(msg.payload.decode())
        timestamp = message['timestamp']
        device_id = message['device_id']
        data = message['data']

        # Prepare the data entry
        data_entry = {
            "Timestamp": timestamp,
            "Device ID": device_id,
            **data
        }

        # Append the data entry to the list
        data_list.append(data_entry)

# Function to start data collection
def start_data_collection():
    global collecting_data, data_list
    collecting_data = True
    data_list = []  # Reset the data list for a new session
    print("Data collection started...")

# Function to stop data collection and save data to Excel
def stop_data_collection():
    global collecting_data, data_list, file_name

    collecting_data = False
    print("Data collection stopped.")

    if data_list:
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(data_list)

        # Determine if the Excel file exists
        if not os.path.isfile(file_name):
            with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        else:
            with pd.ExcelWriter(file_name, engine='openpyxl', mode='a') as writer:
                df.to_excel(writer, index=False, sheet_name=f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        print(f"Data saved to {file_name}")

# Set up MQTT client and callbacks
client = mqtt.Client()
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Subscribe to the topic
client.subscribe(MQTT_TOPIC)

# Function to start the MQTT loop
def start_mqtt_loop():
    client.loop_start()

# Function to stop the MQTT loop
def stop_mqtt_loop():
    client.loop_stop()

# Example usage
if __name__ == "__main__":
    start_mqtt_loop()  # Start listening for messages

    start_data_collection()
    
    # Use a separate thread to handle input so the main thread can continue running the MQTT loop
    def handle_input():
        input("Press Enter to stop data collection...")
        print("Waiting 60 seconds before stopping data collection...")
        time.sleep(60)  # Wait for 5 seconds
        stop_data_collection()
        stop_mqtt_loop()

    input_thread = threading.Thread(target=handle_input)
    input_thread.start()
    input_thread.join()  # Wait for the input thread to finish before exiting the script
