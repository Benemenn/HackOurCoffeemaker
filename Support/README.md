# BIPHackYourCoffeemaschine - SaveData.py
Hack Your Coffeemaschine
# Data Logging with MQTT - README
## Overview
This project is designed to log data received from MQTT topics related to energy monitoring and coffee machine events. The data is stored in CSV files for further analysis. The script listens to three MQTT topics:

Energy Data Topic (bipfinnland/monitoring11/data): Receives energy-related data from devices.
Coffee Data Topic (bipfinnland/hackyourcoffee11/data): Receives data about coffee machine events.
Control Topic (bipfinnland/monitoring11/control): Controls the start and stop of data recording.
The script uses asynchronous programming to handle multiple MQTT clients simultaneously, ensuring that data from different topics is processed concurrently.

## How It Works
CSV File Initialization
The script initializes two CSV files: energy_data.csv and coffee_data.csv.
CSV Creation: If the CSV files do not already exist, the script creates them and writes the appropriate headers. This ensures that the files are ready to store incoming data as soon as the script starts.
## MQTT Client Setup
The script creates three MQTT clients, each subscribed to a different topic.
The clients connect to the specified MQTT broker and listen for incoming messages.
## Data Handling
Energy Data: When a message is received on the energy topic, the script decodes the JSON payload and extracts relevant fields (e.g., voltage, current, power). This data is appended to the energy_data.csv file.
Coffee Data: Messages on the coffee topic contain information about coffee machine events, such as labels and products. This data is saved to the coffee_data.csv file.
Control Messages: The control topic is used to start or stop the data recording. Sending a "Start" command will enable data saving, while an "End" command will disable it.
## Control Mechanism
The control topic allows dynamic control over when data recording should happen. For example, you can start recording when the system is in an operational state and stop when it's idle.
The control mechanism is particularly useful for managing large data sets and ensuring that only relevant data is logged.
## Event Loop Handling
The script is designed to run on different operating systems, including Windows. On Windows, the event loop policy is adjusted to ensure compatibility.
## How to Customize the Code
1. Change the MQTT Broker
If you're using a different MQTT broker, modify the self.BROKER variable in the DataLogging class to point to the correct IP address or hostname.
2. Adjust the MQTT Topics
Update the self.TOPIC_ENERGY, self.TOPIC_COFFEE, and self.TOPIC_CONTROL variables if your topics differ from the default ones used in this script.
3. Modify CSV File Structure
If you need to log additional fields or change the structure of the CSV files, modify the initialize_csv method and the corresponding data handling methods (handle_energy_message and handle_label_message).
4. Implement Custom Control Logic
The control logic can be customized by modifying the handle_control_message method. You can add more commands or change the behavior based on different control messages.
Using Node-RED for Control
To manage the recording process, you can use Node-RED, a flow-based development tool for visual programming. Here's how you can use Node-RED to send control messages:

# Install Node-RED: Follow the installation instructions on the Node-RED website.

## Create a Flow:

Set up an MQTT output node in Node-RED and configure it to connect to your MQTT broker.
Create inject nodes (or Buttons) to send JSON payloads with {"control": "Start"} and {"control": "End"} messages.
Connect the Nodes:
Connect the inject or button to the mqtt output node. Configure the mqtt topic in the output node to match the topic defined on your Energy-Monitoringbox.
Deploy and Test.

Deploy the flow in Node-RED.
Use the inject nodes to send start and stop commands to your MQTT broker, and observe how the data logging responds.
Conclusion
This script provides a flexible and extensible framework for logging data from MQTT topics. By customizing the MQTT topics, CSV file structure, and control logic, you can adapt the script to fit your specific requirements. Using Node-RED for control messages adds an additional layer of interactivity, allowing you to manage the data logging process with ease.
