# Triage-support
Triage Support is a real-time clinical monitoring platform designed for emergency departments and triage units.The system continuously tracks patient vital signs using wearable 
wristbands, pulse oximeters, and temperature sensors. By comparing live telemetry streams against configurable baseline limits, it automatically identifies physiological 
anomalies. When readings breach safe boundaries, the dashboard creates an urgent alert for nursing staff to re-evaluate the patient. From the dashboard, staff can dynamically 
adjust Emergency Severity Index ($\text{ESI}$) priority ranks, acknowledge and reset alerts once vitals stabilize, or check in patients to process their admission and clear them 
from active triage.

⚡ Key CapabilitiesMulti-Sensor 

Telemetry: Continuous tracking of Heart Rate , Blood Oxygen Saturation , and Body Temperature.

Automated Anomaly Detection: Flags readings exceeding safe boundaries to prompt immediate nursing intervention.

Priority Queuing: Automatically moves critical patients with active alerts to the top of the board.

Integrated Actions: menu to adjust  priority, clear resolved alerts, or complete patient admissions.

Hardware & Simulation Support: Connects wirelessly via Bluetooth Low Energy (BLE) to ESP32 hardware or runs an integrated multi-patient telemetry simulator.

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


## 🎮 Give it a try

1.go to the web app using the link below

https://triagesupport.streamlit.app/

2.This website wont be connected to any bands so you wont be able to see the vitals change in real time

3.Try adding a patient by pressing the add patient button, change the values for the: Baseline Vitals, ESL priority, and add a name and band ID.

4.next try select that same patient and press the manage selected patient button.

5.you can change the patients ESI, return its status to normal or check in the patient and remove them from the dashboard.


## Future Ideas:
- take advantage of AI app builders to allow for easy setup on other systems.
  
- Integrate AI into the nurse alert system to cover more possibilities on how the vitals can change.
  
- measure respiratory rate and blood pressure
  
- Use personalized sensors to reduce the size of the band, and increase the accuracy of the readings








