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
MQTT_TOPIC_DATA = "bipfinnland/monitoring9/data"  
MQTT_TOPIC_ESP = "bipfinnland/monitoring9/esp"    

# Global variables to manage data collection
collecting_data = False
data_list = []
file_name = "coffee_machine_data.xlsx"
ai_training_file = "ai_training_data.xlsx"  # File for AI training data

# Global variables to track button presses and slider position
button_left_pressed = False
button_right_pressed = False
slider_position = "None"

# Variables to track Power Low values
power_low_sum = 0
is_tracking_power = False  # Start tracking after second >200
first_threshold_passed = False  # To ensure we ignore the first >200 crossing
second_threshold_ready = False  # To ensure tracking only after the second >200 crossing

# Callback when the client receives a message from the server
def on_message(client, userdata, msg):
    global data_list, collecting_data, button_left_pressed, button_right_pressed, slider_position
    global power_low_sum, is_tracking_power, first_threshold_passed, second_threshold_ready
    
    if collecting_data:
        # Parse the JSON message
        message = json.loads(msg.payload.decode())

        # Check which topic the message came from
        if msg.topic == MQTT_TOPIC_DATA:
            timestamp = message.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            device_id = message.get('device_id', 'unknown')
            data = message.get('data', {})

            # Track Power Low values and sum when >200 after ignoring the first >200
            power_low_value = data.get('Power Low', 0)

            if power_low_value > 200 and not first_threshold_passed:
                first_threshold_passed = True  # Ignore the first time >200 is crossed
                print(f"[DEBUG] Ignored first threshold crossing with Power Low = {power_low_value}")
            elif power_low_value < 200 and first_threshold_passed and not second_threshold_ready:
                # If it goes below 200 after the first threshold pass, we prepare for the second tracking
                second_threshold_ready = True
                print(f"[DEBUG] Ready for second threshold crossing after Power Low went below 200")
            elif power_low_value > 200 and second_threshold_ready and not is_tracking_power:
                # Now we start tracking sums after the second crossing
                is_tracking_power = True
                print(f"[DEBUG] Started tracking Power Low values after second threshold crossing: {power_low_value}")
            elif power_low_value < 200 and is_tracking_power:
                is_tracking_power = False  # Stop tracking and reset
                print(f"[DEBUG] Stopped tracking Power Low values at: {power_low_value}")

            if is_tracking_power:
                power_low_sum += power_low_value
                print(f"[DEBUG] Adding Power Low value: {power_low_value}, Current Sum: {power_low_sum}")

            # Prepare the data entry (without buttons and slider position)
            data_entry = {
                "Timestamp": timestamp,
                "Device ID": device_id,
                "Voltage": data.get('Voltage', 0),
                "Current Low": data.get('Current Low', 0),
                "Current High": data.get('Current High', 0),
                "Power Low": data.get('Power Low', 0),
                "Power High": data.get('Power High', 0),
                "Energy Low": data.get('Energy Low', 0),
                "Energy High": data.get('Energy High', 0),
                "Frequency": data.get('Frequency', 0),
                "Power Factor": data.get('Power Factor', 0),
                "Alarm Status": data.get('Alarm Status', 0)
            }
            data_list.append(data_entry)

        elif msg.topic == MQTT_TOPIC_ESP:
            # For the ESP topic, collect button and slider position data
            button_left = message.get('ButtonCoffeeLeft', False)
            button_right = message.get('ButtonCoffeeRight', False)
            slider_position = message.get('SliderPosition', slider_position)  # Update slider position if provided

            # Track if the left or right button was pressed
            if button_left:
                button_left_pressed = True
                print(f"[DEBUG] Left button pressed.")
            if button_right:
                button_right_pressed = True
                print(f"[DEBUG] Right button pressed.")

# Function to start data collection
def start_data_collection():
    global collecting_data, data_list, power_low_sum, is_tracking_power, first_threshold_passed, second_threshold_ready
    collecting_data = True
    data_list = []  # Reset the data list for a new session
    power_low_sum = 0  # Reset the power low sum for the new session
    is_tracking_power = False
    first_threshold_passed = False  # Reset the threshold flag
    second_threshold_ready = False  # Reset second threshold readiness
    print("[DEBUG] Data collection started...")

# Function to stop data collection, process power low, and save AI training data
# Function to stop data collection, process power low, and save AI training data
def stop_data_collection():
    global collecting_data, data_list, file_name, button_left_pressed, button_right_pressed, slider_position, power_low_sum

    collecting_data = False
    print("[DEBUG] Data collection stopped.")

    # Process the cup type based on button presses and slider position
    cup_type = None
    if button_left_pressed and slider_position == "Left":
        cup_type = "single_small"
    elif button_left_pressed and slider_position == "Right":
        cup_type = "single_large"
    elif button_right_pressed and slider_position == "Left":
        cup_type = "double_small"
    elif button_right_pressed and slider_position == "Right":
        cup_type = "double_large"

    # Check if we have data in data_list
    if not data_list:
        print("[ERROR] No data collected!")
        return

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data_list)

    # Save regular session data to the file
    session_name = f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_name = session_name[:31]  # Limit sheet name to 31 characters

    # Create or append to the Excel file
    if not os.path.isfile(file_name):
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=session_name)
        print(f"[DEBUG] Created new file: {file_name} and saved session data")
    else:
        with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            df.to_excel(writer, index=False, sheet_name=session_name)
        print(f"[DEBUG] Data saved to {file_name}")

    # Save to the AI training file even if the last Power Low value is 0 but there's a valid sum
    if power_low_sum > 0:  # Check if any valid sum was accumulated
        print(f"[DEBUG] Saving AI training data - Power Low Sum: {power_low_sum}, Cup Type: {cup_type if cup_type else 'Unknown'}")

        # Load existing AI training data or create a new one
        if not os.path.isfile(ai_training_file):
            ai_training_df = pd.DataFrame(columns=["Power Low Sum", "Cup Type"])
            print(f"[DEBUG] Created new AI training file: {ai_training_file}")
        else:
            ai_training_df = pd.read_excel(ai_training_file)

        # Add new row with Power Low Sum and Cup Type
        new_row = pd.DataFrame({"Power Low Sum": [power_low_sum], "Cup Type": [cup_type if cup_type else "Unknown"]})

        # Use concat instead of append (since append is deprecated)
        ai_training_df = pd.concat([ai_training_df, new_row], ignore_index=True)

        # Save the updated AI training data
        with pd.ExcelWriter(ai_training_file, engine='openpyxl', mode='w') as writer:  # Mode 'w' for overwriting
            ai_training_df.to_excel(writer, index=False, sheet_name="AI_Training")

        print(f"[DEBUG] AI training data saved to {ai_training_file}")
    else:
        print("[ERROR] No valid Power Low data accumulated. Check the tracking logic.")


# Set up MQTT client and callbacks
client = mqtt.Client()
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Subscribe to both topics
client.subscribe(MQTT_TOPIC_DATA)  # For general data
client.subscribe(MQTT_TOPIC_ESP)   # For ESP button and slider data

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
        print("[DEBUG] Waiting 80 seconds before stopping data collection...")
        time.sleep(110)  # Collect data for 80 seconds
        stop_data_collection()
        stop_mqtt_loop()

    input_thread = threading.Thread(target=handle_input)
    input_thread.start()
    input_thread.join()  # Wait for the input thread to finish before exiting the script
