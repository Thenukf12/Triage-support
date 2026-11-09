# Triage-support
Nathacks  2026 project- Triage support

Triage support is a app that monitors patients vital sign using a wristband, finger clip and temperature sensor

the app receives the live data and compares it to baseline max and min values, if any vitals do exceed the safe range

it creates an alert for a nurse to reassess the patients condition. From there they can choose to change their

ESI priority, return their status to normal or remove them from the dashboard.

## 📁 Repository Files

* `app.py`: Core Streamlit dashboard application UI, sorting logic, and interactive grid fragment[cite: 3].
* `patient_monitoring.py`: Clinical monitoring class handling threshold checks, sudden change counters, and alert state machines[cite: 3].
* `BLE_EPS32_Vital_Reader.py`: Async BLE receiver script connecting to ESP32 hardware and updating the shared JSON bridge[cite: 3].
* `python telemetry_simulator.py`: Multi-patient simulation script generating realistic telemetry and critical spikes[cite: 3].
* `live_vitals.json`: Shared atomic JSON file bridge linking hardware/simulator data to Streamlit[cite: 3].



Give it a try~

1.go to the web app using the link below

https://triagesupport.streamlit.app/

2.This website wont be connected to any bands so you wont be able to see the vitals change in real time

3.Try adding a patient by pressing the add patient button, change the values for the: Baseline Vitals, ESL priority, and add a name and band ID.

4.next try select that same patient and press the manage selected patient button.

5.you can change the patients ESL, return its status to normal or check in the patient and remove them from the dashboard.
