import json
import os
import random
import time

BAND_IDS = ["BAND-1", "BAND-2", "BAND-3"]


def run_simulator():
    print("📡 Starting Multi-Patient Telemetry Simulator...")
    print(" - BAND-1: Normal Vitals")
    print(" - BAND-2: 🚨 CRITICAL ALERT (Severe Tachycardia > 130 BPM)")
    print(" - BAND-3: Normal Vitals")

    while True:
        now = time.time()
        payload = {
            "BAND-1": {
                "heart_rate": random.randint(132, 150),
                "spo2": random.randint(97, 99),
                "temperature": round(random.uniform(36.5, 37.0), 1),
                "timestamp": now,
            },
            "BAND-2": {
                "heart_rate": random.randint(132, 145),
                "spo2": random.randint(80, 85),
                "temperature": round(random.uniform(37.1, 37.5), 1),
                "timestamp": now,
            },
            "BAND-3": {
                "heart_rate": random.randint(68, 74),
                "spo2": random.randint(98, 100),
                "temperature": round(random.uniform(36.4, 36.8), 1),
                "timestamp": now,
            },
        }

        # Safe file write wrapped in try/except for Windows file locking
        try:
            temp_file = "live_vitals.json.tmp"
            with open(temp_file, "w") as f:
                json.dump(payload, f, indent=2)
            os.replace(temp_file, "live_vitals.json")

            print(
                f"[{time.strftime('%H:%M:%S')}] Telemetry updated for BAND-1,"
                " BAND-2 (CRITICAL), BAND-3"
            )
        except PermissionError:
            # Skip write if file is locked by app.py or OneDrive for a fraction of a second
            pass

        time.sleep(1)


if __name__ == "__main__":
    run_simulator()