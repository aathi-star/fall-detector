# Fall Detection IoT + ML

This project demonstrates an end-to-end fall detection system using an **ESP32** microcontroller with an **MPU6050** accelerometer, **MQTT** messaging, and a **Python machine learning** pipeline.

## Hardware

- ESP32 development board
- MPU6050 accelerometer/gyroscope
- Wiring:
  - VCC → 3.3V
  - GND → GND
  - SDA → GPIO21
  - SCL → GPIO22

## Overview

The ESP32 continuously reads acceleration values from the MPU6050 and publishes them as JSON messages to an MQTT broker. A Python application subscribes to the stream, builds feature vectors over sliding windows, and applies an SVM model to detect falls in real-time.

## Setup

1. **ESP32**
   - Open `esp32/esp32_mpu6050_mqtt.ino` in the Arduino IDE.
   - Install required libraries: `WiFi`, `PubSubClient`, `Wire`, and `MPU6050`.
   - Update Wi-Fi credentials and MQTT broker address.
   - Flash the sketch to the ESP32.

2. **MQTT Broker**
   - Install Mosquitto or another MQTT broker and ensure it is running.

3. **Python Environment**
   ```bash
   cd python
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Train the model**
   ```bash
   python train_model.py
   ```

5. **Run real-time inference**
   ```bash
   python realtime_infer.py
   ```

## Example Output

```
[12:34:10] Normal p=0.08
[12:34:12] FALL p=0.92
*** ALERT: Possible fall detected!
```

The alert is also appended to `logs/alerts.log` for later analysis.
