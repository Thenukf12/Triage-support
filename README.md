# Triage-support
Nathacks  2026 project- Triage support

Triage support is a app that monitors patients vital sign using a wristband, finger clip and temperature sensor

the app receives the live data and compares it to baseline max and min values, if any vitals do exceed the safe range

it creates an alert for a nurse to reassess the patients condition. From there they can choose to change their

ESI priority, return their status to normal or remove them from the dashboard.

## 📁 Repository Files

* `app.py`: Core Streamlit dashboard application UI, sorting logic, and interactive grid fragment.
* `patient_monitoring.py`: Clinical monitoring class handling threshold checks, sudden change counters, and alert state machines.
* `BLE_EPS32_Vital_Reader.py`: Async BLE receiver script connecting to ESP32 hardware and updating the shared JSON bridge.
* `python telemetry_simulator.py`: Multi-patient simulation script generating realistic telemetry and critical spikes.
* `live_vitals.json`: Shared atomic JSON file bridge linking hardware/simulator data to Streamlit.
*`dht_temp__sensor`: Introduced the DHT 11 temperature sensor, contains helper functions for the main ESP32 code to setup the sensor and update the values.
* `max30102_sensor`: Introduced the MAX30102 heart rate and SpO2 sensor, contains helper functions for the main ESP32 code to setup the sensor and update the values.
* `OLED_ui`: Introduced the OLED Display Screen, contains helper functions for the main ESP32 code to setup the clear display and print the text on the screen.
* `main_esp32_ini`: Contains the primary code to set up the GATT Server connection through Bluetooth, calls on each sensor function to update the values and send them into channels to be received by a device.


Give it a try~

1.go to the web app using the link below

https://triagesupport.streamlit.app/

2.This website wont be connected to any bands so you wont be able to see the vitals change in real time

3.Try adding a patient by pressing the add patient button, change the values for the: Baseline Vitals, ESL priority, and add a name and band ID.

4.next try select that same patient and press the manage selected patient button.

5.you can change the patients ESL, return its status to normal or check in the patient and remove them from the dashboard.



**the code in this projected was made using the reference of:**

Gemini AI

Streamlit Library documentation

VScode

DTRobot MAX30102 documentation





