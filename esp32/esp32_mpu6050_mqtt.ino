#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <MPU6050.h>

// Replace with your network credentials
const char* WIFI_SSID = "YOUR_SSID";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";

// MQTT broker details
const char* MQTT_HOST = "192.168.1.100"; // change to your broker
const int   MQTT_PORT = 1883;
const char* MQTT_TOPIC = "iot/falldetector/accel";

WiFiClient espClient;
PubSubClient mqttClient(espClient);
MPU6050 mpu;

unsigned long lastPublish = 0;
const int PUBLISH_INTERVAL_MS = 40; // ~25 Hz

void setupWiFi() {
  delay(10);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    mqttClient.connect("esp32-fall-detector");
    if (!mqttClient.connected()) {
      delay(1000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); // SDA=21, SCL=22
  mpu.initialize();
  setupWiFi();
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
}

void loop() {
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  unsigned long now = millis();
  if (now - lastPublish >= PUBLISH_INTERVAL_MS) {
    lastPublish = now;

    int16_t rawAx, rawAy, rawAz;
    mpu.getAcceleration(&rawAx, &rawAy, &rawAz);
    const float g = 9.80665;
    float ax = (rawAx / 16384.0) * g;
    float ay = (rawAy / 16384.0) * g;
    float az = (rawAz / 16384.0) * g;

    char payload[128];
    snprintf(payload, sizeof(payload),
             "{\"ts\":%lu,\"ax\":%.3f,\"ay\":%.3f,\"az\":%.3f}",
             now, ax, ay, az);
    mqttClient.publish(MQTT_TOPIC, payload);
  }
}
