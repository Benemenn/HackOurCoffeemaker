#include <Arduino.h>
#include <ArduinoJson.h>
#include <arduino_stopwatch.h>
#include "esp_log.h"
#include "wifi/wifiCredentials.h"
#include "wifi/wifi_handler.h"
#include "mqtt/mqtt_handler.h"
#include "ntp/ntp_handler.h"
#include "sensors/ads1115_continuous.h"
#include "sensors/debounced_button.h"
#include "sensors/ldr_blink_sensor.h"
#include "sensors/threshold_sensor.h"
#include "sensors/slider_button.h"

using ArduinoStopwatch::Stopwatch32MS;

// logging:
static const char* ESP_LOG_TAG = "ESP";
// wifi:
static WiFiHandler wifiHandler("IOT-Coffeemaker");
// mqtt:
static MqttHandler mqttHandler("IOT-Coffeemaker");
static const IPAddress MQTT_BROKER_IP(192, 168, 178, 21); // broker on the BaristaBandwidth network
static const u16_t MQTT_BROKER_PORT = 1883;
Stopwatch32MS publishWatch;
static const u32_t PUBLISH_INTERVAL_MILLIS = 500;
static const char* PUBLISH_TOPIC = "bipfinnland/monitoring9/esp";
// json:
static JsonDocument jsonDoc;
// NTP:
static const IPAddress NTP_SERVER_IP(192, 168, 178, 21);
static const u16_t NTP_UPDATE_INTERVAL_MILLIS = 60000;
static const u32_t TIMEZONE_OFFSET = 7200;
NtpHandler ntpHandler(NTP_SERVER_IP, NTP_UPDATE_INTERVAL_MILLIS, TIMEZONE_OFFSET);
// ADC:
static const int I2C_SCL_PIN = 15;
static const int I2C_SDA_PIN = 16;
static const u8_t ADC_FILTER_SIZE = 4;
static Ads1115Continuous adcConverter;
static const u8_t LIGHT_LEFT_CHANNEL = 0;
static const u8_t LIGHT_RIGHT_CHANNEL = 1;
static const u8_t WATER_LEVEL_CHANNEL = 2;
// LDRs:
static LdrBlinkSensor sensorLightLeft;
static LdrBlinkSensor sensorLightRight;
// Water Level:
static const u16_t WATER_LEVEL_ON_THRESHOLD = 13000;
static const u16_t WATER_LEVEL_OFF_THRESHOLD = 7000;
static const u8_t WATER_LEVEL_FILTER_SIZE = 3;
static ThresholdSensor switchWaterLevel(WATER_LEVEL_ON_THRESHOLD, WATER_LEVEL_OFF_THRESHOLD, WATER_LEVEL_FILTER_SIZE);
// Buttons:
static const int BUTTON_COFFEE_LEFT_PIN = 33;
static const int BUTTON_COFFEE_RIGHT_PIN = 17;
static const int BUTTON_SLIDER_LEFT_PIN = 21;
static const int BUTTON_SLIDER_RIGHT_PIN = 18;
static DebouncedButton buttonCoffeeLeft(BUTTON_COFFEE_LEFT_PIN, ButtonType::NORMALY_CLOSED, InputType::ENABLE_PULLUP);
static DebouncedButton buttonCoffeeRight(BUTTON_COFFEE_RIGHT_PIN, ButtonType::NORMALY_CLOSED, InputType::ENABLE_PULLUP);
static DebouncedButton buttonSliderLeft(BUTTON_SLIDER_LEFT_PIN, ButtonType::NORMALY_CLOSED, InputType::ENABLE_PULLUP);
static DebouncedButton buttonSliderRight(BUTTON_SLIDER_RIGHT_PIN, ButtonType::NORMALY_CLOSED, InputType::ENABLE_PULLUP);
static SliderButton slider;

void setup(){
    // Serial:
    Serial.begin(115200);
    ESP_LOGI(ESP_LOG_TAG, "start of setup()");
    // ADC:
    Wire.setPins(I2C_SDA_PIN, I2C_SCL_PIN);
    if (!adcConverter.begin(true, true, true, false, ADC_FILTER_SIZE)) {
        ESP_LOGE(ESP_LOG_TAG, "Failed to initialize ADS1115.");
        delay(5000);
        exit(0);
    }
    // WiFi:
    if(!wifiHandler.connect(WIFI_SSID, WIFI_PWD)) {
        delay(5000);
        exit(0);
    }
    // NTP:
    if(!ntpHandler.begin()) {
        delay(5000);
        exit(0);
    }
    // Mqtt:
    if(!mqttHandler.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT)) {
        // no error
    }
    publishWatch.restart();
    // Json:
    jsonDoc["ButtonCoffeeLeft"] = false;
    jsonDoc["ButtonCoffeeRight"] = false;
    jsonDoc["SliderPosition"] = "None";
    jsonDoc["LightLeft"] = "OFF";
    jsonDoc["LightRight"] = "OFF";
    jsonDoc["WaterSwitch"] = false;
    jsonDoc["Timestamp"] = ntpHandler.getFormattedTime();
    //
    ESP_LOGI(ESP_LOG_TAG, "end of setup()");
}

void loop() {
    adcConverter.update();
    buttonCoffeeLeft.update();
    buttonCoffeeRight.update();
    buttonSliderLeft.update();
    buttonSliderRight.update();
    sensorLightLeft.update(adcConverter, LIGHT_LEFT_CHANNEL);
    sensorLightRight.update(adcConverter, LIGHT_RIGHT_CHANNEL);
    switchWaterLevel.update(adcConverter, WATER_LEVEL_CHANNEL);
    slider.update(buttonSliderLeft.isPressed(), buttonSliderRight.isPressed());
    mqttHandler.update();
    ntpHandler.update();

    if (publishWatch.getTimeSinceStart() >= PUBLISH_INTERVAL_MILLIS) {
        ESP_LOGI(ESP_LOG_TAG, "Cycletime: %ims", publishWatch.getTimeSinceStart());
        publishWatch.restart();
        // update jsonDoc:
        jsonDoc["ButtonCoffeeLeft"] = buttonCoffeeLeft.isPressed();
        jsonDoc["ButtonCoffeeRight"] = buttonCoffeeRight.isPressed();
        jsonDoc["SliderPosition"] = slider.getStateAsString();
        jsonDoc["LightLeft"] = sensorLightLeft.getStateString();
        jsonDoc["LightRight"] = sensorLightRight.getStateString();
        jsonDoc["WaterSwitch"] = switchWaterLevel.getState();
        jsonDoc["Timestamp"] = ntpHandler.getFormattedTime();
        // publish:
        mqttHandler.publish(PUBLISH_TOPIC, jsonDoc);
    }
}