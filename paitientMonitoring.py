import statistics 


def send_alert(alert):

    # Temporary signal for testing
    print("ALERT SIGNAL SENT")
    print(alert)


class PatientMonitoring:

    def __init__(self, patientId, baseline):
        self.patientId = patientId
        self.baseline = baseline.copy()  # take a copy on initial vitals
        self.recent_vitals = baseline.copy() #store the most recent vitals
        self.readingHistory = [] #store the reading history of the patient
        self.activeAlerts = {} #store the active alerts for the patient
        self.activeConditions = {}
        self.resolvedConditions = {}
        # Threshold limits for each vital sign
        self.criticalThresholds = {
            "bpm": {
                "low": None,
                "high": None
            },
            "temperature": {
                "low": None,
                "high": None
            },
            "spo2": {
                "low": None,
                "high": None
            }
                    # Settings for detecting sudden changes
        }

        self.change_limits = {
            "bpm": None,
            "temperature": None,
            "spo2": None
        }

        # Count consecutive readings that show a sudden change
        self.change_counters = {
            "bpm": 0,
            "temperature": 0,
            "spo2": 0
        }
        # Number of consecutive readings needed
        self.required_readings = 3

        # Minimum change between consecutive readings
        self.jump_limits = {
            "bpm": None,
            "temperature": None,
            "spo2": None
        }

        # Tracks whether a sudden change has started
        self.sudden_change_active = {
            "bpm": False,
            "temperature": False,
            "spo2": False
        }

        

        
        
    def checkThresholds(self):

        # Check each vital sign
        for vital, value in self.recent_vitals.items():

            # Get the upper and lower limits
            low = self.criticalThresholds[vital]["low"]
            high = self.criticalThresholds[vital]["high"]

            # Create alert identifiers
            low_alert = vital + "_low"
            high_alert = vital + "_high"

            # Check if the reading is too low
            if low is not None and value < low:

                self.generate_alert(
                    low_alert,
                    vital,
                    value,
                    vital + " is below its configured threshold"
                )

            else:
                # The low condition has returned to normal
                self.activeConditions.pop(low_alert, None)
                self.resolvedConditions.pop(low_alert, None)

            # Check if the reading is too high
            if high is not None and value > high:

                self.generate_alert(
                    high_alert,
                    vital,
                    value,
                    vital + " is above its configured threshold"
                )

            else:
                # The high condition has returned to normal
                self.activeConditions.pop(high_alert, None)
                self.resolvedConditions.pop(high_alert, None)


    def check_changes(self, new_reading):

        # Check each vital sign
        for vital, value in new_reading.items():

            # Get the previous reading
            previous = self.recent_vitals[vital]

            # Get the original baseline
            baseline = self.baseline[vital]

            # Get the configured limits
            jump_limit = self.jump_limits[vital]
            change_limit = self.change_limits[vital]

            # Skip if the required limits are not configured
            if jump_limit is None or change_limit is None:
                continue

            # Calculate the difference from the previous reading
            jump = abs(value - previous)

            # Check whether a sudden jump has occurred
            if not self.sudden_change_active[vital]:

                if jump >= jump_limit:
                    self.sudden_change_active[vital] = True

                    # Count the first reading of the change
                    self.change_counters[vital] = 1

            else:

                # Check whether the reading remains different
                # from the original baseline
                difference = abs(value - baseline)

                if difference >= change_limit:

                    self.change_counters[vital] += 1

                else:

                    # The change has returned to baseline range
                    self.change_counters[vital] = 0
                    self.sudden_change_active[vital] = False

            # Check if enough consecutive readings occurred
            if self.change_counters[vital] == self.required_readings:

                self.generate_alert(
                    vital + "_sudden_change",
                    vital,
                    value,
                    vital + " has shown a sudden persistent change"
                )


    def receive_reading(self, bpm, temperature, spo2):

        # Store the new readings
        new_reading = {
            "bpm": bpm,
            "temperature": temperature,
            "spo2": spo2
        }

        # Check for sudden changes BEFORE updating recent_vitals
        self.check_changes(new_reading)

        # Save the readings
        self.readingHistory.append(new_reading)

        # Update the most recent readings
        self.recent_vitals = new_reading.copy()

        # Check configured thresholds
        self.checkThresholds()
    
    
    def generate_alert(self, alert_type, vital, reading, reason):

        # Check if this condition is already happening
        if alert_type in self.activeConditions:
            return

        # Check if this condition was already resolved
        # but has not returned to normal yet
        if alert_type in self.resolvedConditions:
            return

        # Record that this condition is happening
        self.activeConditions[alert_type] = True

        # Create the alert signal
        alert = {
            "patient_id": self.patientId,
            "alert_type": alert_type,
            "vital": vital,
            "reading": reading,
            "reason": reason
        }

        # Store the active alert
        self.activeAlerts[alert_type] = alert

        # Send the signal to the external system
        send_alert(alert)


    def resolve_alert(self, alert_type):

        # Check if the alert exists
        if alert_type in self.activeAlerts:

            # Remove the alert from active alerts
            del self.activeAlerts[alert_type]

            # Check if the condition is still happening
            if alert_type in self.activeConditions:

                # Remember that the nurse resolved this alert
                self.resolvedConditions[alert_type] = True

            print("Alert manually resolved")

        else:

            print("Alert not found")
        




patient7 = PatientMonitoring(
    107,
    {
        "bpm": 75,
        "temperature": 37.0,
        "spo2": 98
    }
)

# # Set example thresholds for testing
# patient7.criticalThresholds["bpm"]["high"] = 120

# # Simulate sensor readings
# patient7.receive_reading(80, 37.0, 98)
# patient7.receive_reading(85, 37.0, 98)
# patient7.receive_reading(125, 37.0, 98)

# # Nurse manually resolves the alert
# patient7.resolve_alert("bpm_high")

# # Patient still has an abnormal BPM
# patient7.receive_reading(130, 37.0, 98)

# # First abnormal reading
# patient7.receive_reading(125, 37.0, 98)

# # Nurse resolves the alert
# patient7.resolve_alert("bpm_high")

# # Still abnormal: should NOT send another alert
# patient7.receive_reading(130, 37.0, 98)

# # Returns to normal: resets the condition
# patient7.receive_reading(90, 37.0, 98)

# # Becomes abnormal again: SHOULD send a new alert
# patient7.receive_reading(125, 37.0, 98)