# Smart Coffee Machine Project

## Overview

This project involves the enhancement of a standard coffee machine by integrating it with smart electronics and data-driven features. Our goal is to develop a coffee machine that can monitor user behavior, optimize energy usage, and offer predictive maintenance capabilities, all while providing a seamless and personalized coffee experience. The project uses an ESP-32 microcontroller and leverages MQTT for data communication, along with a deep learning model to analyze and predict usage patterns.

## Project Goals

- **Smart Monitoring**: Track button presses and monitor which of the four types of coffee is selected.
- **Data Logging**: Implement a system to log usage data, which will be used to train and test a deep learning model.
- **Predictive Features**: Develop a model to predict user behavior and optimize machine operation, including preemptively heating water.
- **User Interaction**: Enable wireless communication with the coffee machine to allow remote control and scheduling of coffee brewing.
- **Sustainability**: Explore options for reducing the coffee machine’s energy consumption through smarter operation.

## Components

- **ESP-32 Microcontroller**: The core of our smart system, used for monitoring button presses and controlling the coffee machine.
- **Node-RED**: Used for backend and frontend data logging and visualization.
- **MQTT**: Facilitates communication between the coffee machine and the user’s devices.
- **Deep Learning Model**: Trained on usage data to predict user behavior and optimize machine operation.
- **Magnetic Circuit**: Added to monitor lid opening and closing.

## To-Do List

### 1. Connect to the ESP-32
- Establish a connection with the ESP-32 on board.
- Implement a system to detect button presses.
- Use this system to collect data for training the deep learning model.

### 2. Test Configurations
- Experiment with different configurations to gather testing data.
- Analyze the data to ensure it is suitable for training the model.

### 3. Data Logging via Node-RED
- Set up Node-RED for backend and frontend logging of usage data.
- Ensure the data is correctly logged and visualized.

### 4. Model Testing and Deployment
- Begin testing the deep learning model with collected data.
- Integrate the model into the system to allow for "plug and play" functionality.

### 5. Add Magnetic Circuit 
- Implement a magnetic circuit to monitor the opening and closing of the lid.
- Ensure it works seamlessly with the existing system.

### 6. Expand ESP-32 Functionality
- If not enough pins are available on the current ESP-32, add a second ESP-32.
- Establish communication between the two ESP-32 units.

### 7. Detecting wether there is a cup of coffee via LEd?

### 7. Control the Heater
- Investigate the possibility of turning the heater on and off using minimally invasive electronics.
- Implement this functionality if feasible.


