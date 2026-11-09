# import asyncio
# import json
# from bleak import BleakClient

# # MAC Address of your ESP32 V2
# MAC_ADDRESS = "0c:8b:95:94:99:56"

# # Individual Characteristic UUIDs for each sensor channel
# HEART_RATE_UUID = "31806ba7-3d6b-4302-bc0c-ae0f761df15b"
# SPO2_UUID = "5db163c6-fdd9-4273-b047-0c6e7c65efc3"
# TEMPERATURE_UUID = "5395d099-dd80-4878-888f-6c4add92801d"

# # Global dictionary to track metrics in real time
# latest_vitals = {
#     "heart_rate": "--",
#     "spo2": "--",
#     "temperature": "--",
#     "status": "Connected"
# }

# def save_latest_vitals(hr=None, spo2=None, temp=None):
#     """Updates and writes the latest sensor payload to the JSON bridge file."""
#     global latest_vitals
    
#     if hr is not None:
#         latest_vitals["heart_rate"] = hr
#     if spo2 is not None:
#         latest_vitals["spo2"] = spo2
#     if temp is not None:
#         latest_vitals["temperature"] = temp
        
#     # Write to shared bridge file for Streamlit
#     with open("live_vitals.json", "w") as f:
#         json.dump(latest_vitals, f)

# def notification_handler(sender, data):
#     # Decode the incoming byte data into a readable string safely
#     decoded_value = data.decode("utf-8", errors="ignore").replace("\x00", "").strip()
#     sender_uuid = str(sender.uuid).lower()

#     # Match the incoming notification to its specific characteristic UUID and save
#     if sender_uuid == HEART_RATE_UUID.lower():
#         hr_val = decoded_value.replace("bpm", "").strip()
#         print(f"[SUCCESS] Heart Rate extracted: {hr_val} bpm")
#         save_latest_vitals(hr=hr_val)
        
#     elif sender_uuid == SPO2_UUID.lower():
#         spo2_val = decoded_value.replace("%", "").strip()
#         print(f"[SUCCESS] SpO2 extracted: {spo2_val}%")
#         save_latest_vitals(spo2=spo2_val)
        
#     elif sender_uuid == TEMPERATURE_UUID.lower():
#         temp_val = decoded_value.replace("°C", "").strip()
#         print(f"[SUCCESS] Temperature extracted: {temp_val} °C")
#         save_latest_vitals(temp=temp_val)
        
#     else:
#         print(f"[DEBUG] Received data from unknown UUID {sender_uuid}: {decoded_value}")

# async def main():
#     print(f"Connecting to ESP32 at {MAC_ADDRESS}...")

#     async with BleakClient(MAC_ADDRESS) as client:
#         if client.is_connected:
#             print("[+] Connected successfully to ESP32!")

#             # Start listening for notifications on all three characteristics
#             await client.start_notify(HEART_RATE_UUID, notification_handler)
#             await client.start_notify(SPO2_UUID, notification_handler)
#             await client.start_notify(TEMPERATURE_UUID, notification_handler)

#             print("[*] Listening for live data stream across all channels... Press Ctrl+C to stop.")

#             # Keep the script running to continuously receive notifications
#             while True:
#                 await asyncio.sleep(1)
#         else:
#             print("[-] Failed to connect.")

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("\nDisconnected by user.")







import asyncio
import json
import os
import time
from bleak import BleakClient

# MAC Address of your ESP32 V2
MAC_ADDRESS = "0c:8b:95:94:99:56"
BAND_ID = "BAND-4"

# Individual Characteristic UUIDs for each sensor channel
HEART_RATE_UUID = "31806ba7-3d6b-4302-bc0c-ae0f761df15b"
SPO2_UUID = "5db163c6-fdd9-4273-b047-0c6e7c65efc3"
TEMPERATURE_UUID = "5395d099-dd80-4878-888f-6c4add92801d"

# Global dictionary to track metrics in real time
latest_vitals = {"heart_rate": 75.0, "spo2": 98.0, "temperature": 37.0}


def save_latest_vitals(hr=None, spo2=None, temp=None):
    """Updates and writes the latest sensor payload to the JSON bridge file."""
    global latest_vitals

    try:
        if hr is not None:
            latest_vitals["heart_rate"] = float(hr)
        if spo2 is not None:
            latest_vitals["spo2"] = float(spo2)
        if temp is not None:
            latest_vitals["temperature"] = float(temp)
    except ValueError:
        pass

    # Read existing JSON payload to preserve telemetry from other bands if present
    payload = {}
    if os.path.exists("live_vitals.json"):
        try:
            with open("live_vitals.json", "r") as f:
                payload = json.load(f)
        except Exception:
            payload = {}

    # Nest data under BAND-4 key with current timestamp
    payload[BAND_ID] = {
        "heart_rate": latest_vitals["heart_rate"],
        "spo2": latest_vitals["spo2"],
        "temperature": latest_vitals["temperature"],
        "timestamp": time.time(),
    }

    # Safe atomic write to prevent Windows file lock conflicts with Streamlit
    try:
        temp_file = "live_vitals.json.tmp"
        with open(temp_file, "w") as f:
            json.dump(payload, f, indent=2)
        os.replace(temp_file, "live_vitals.json")
    except PermissionError:
        pass


def notification_handler(sender, data):
    decoded_value = (
        data.decode("utf-8", errors="ignore").replace("\x00", "").strip()
    )
    sender_uuid = str(sender.uuid).lower()

    if sender_uuid == HEART_RATE_UUID.lower():
        hr_val = decoded_value.replace("bpm", "").strip()
        print(f"[SUCCESS] Heart Rate extracted: {hr_val} bpm")
        save_latest_vitals(hr=hr_val)

    elif sender_uuid == SPO2_UUID.lower():
        spo2_val = decoded_value.replace("%", "").strip()
        print(f"[SUCCESS] SpO2 extracted: {spo2_val}%")
        save_latest_vitals(spo2=spo2_val)

    elif sender_uuid == TEMPERATURE_UUID.lower():
        temp_val = decoded_value.replace("°C", "").strip()
        print(f"[SUCCESS] Temperature extracted: {temp_val} °C")
        save_latest_vitals(temp=temp_val)

    else:
        print(
            f"[DEBUG] Unknown UUID {sender_uuid}:"
            f" {decoded_value}"
        )


async def main():
    print(f"Connecting to ESP32 at {MAC_ADDRESS}...")

    async with BleakClient(MAC_ADDRESS) as client:
        if client.is_connected:
            print("[+] Connected successfully to ESP32!")

            await client.start_notify(HEART_RATE_UUID, notification_handler)
            await client.start_notify(SPO2_UUID, notification_handler)
            await client.start_notify(TEMPERATURE_UUID, notification_handler)

            print(
                "[*] Listening for live data stream across all channels..."
                " Press Ctrl+C to stop."
            )

            while True:
                await asyncio.sleep(1)
        else:
            print("[-] Failed to connect.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDisconnected by user.")