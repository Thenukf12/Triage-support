import statistics


def default_send_alert(alert):
    print("ALERT SIGNAL SENT:", alert)


class PatientMonitoring:

    def __init__(self, patientId, baseline, alert_callback=None):
        self.patientId = patientId
        self.baseline = baseline.copy()
        self.recent_vitals = baseline.copy()
        self.readingHistory = []
        self.activeAlerts = {}
        self.activeConditions = {}
        self.resolvedConditions = {}
        self.alert_callback = alert_callback or default_send_alert

        # Default clinical threshold limits
        self.criticalThresholds = {
            "bpm": {"low": 50, "high": 120},
            "temperature": {"low": 35.5, "high": 38.0},
            "spo2": {"low": 92, "high": 100},
        }

        self.change_limits = {"bpm": 15, "temperature": 1.0, "spo2": 3}
        self.jump_limits = {"bpm": 10, "temperature": 0.5, "spo2": 2}

        self.change_counters = {"bpm": 0, "temperature": 0, "spo2": 0}
        self.required_readings = 3
        self.sudden_change_active = {
            "bpm": False,
            "temperature": False,
            "spo2": False,
        }

    def checkThresholds(self):
        for vital, value in self.recent_vitals.items():
            if value is None:
                continue

            low = self.criticalThresholds[vital]["low"]
            high = self.criticalThresholds[vital]["high"]
            low_alert = f"{vital}_low"
            high_alert = f"{vital}_high"

            # LOW THRESHOLD CHECK
            if low is not None and value < low:
                self.generate_alert(
                    low_alert,
                    vital,
                    value,
                    f"{vital.upper()} ({value}) is below threshold ({low})",
                )
            else:
                # Vital returned to normal range (>= low): re-arm low threshold alert
                self.activeConditions.pop(low_alert, None)
                self.activeAlerts.pop(low_alert, None)
                self.resolvedConditions.pop(low_alert, None)

            # HIGH THRESHOLD CHECK
            if high is not None and value > high:
                self.generate_alert(
                    high_alert,
                    vital,
                    value,
                    f"{vital.upper()} ({value}) is above threshold ({high})",
                )
            else:
                # Vital returned to normal range (<= high): re-arm high threshold alert
                self.activeConditions.pop(high_alert, None)
                self.activeAlerts.pop(high_alert, None)
                self.resolvedConditions.pop(high_alert, None)

    def check_changes(self, new_reading):
        for vital, value in new_reading.items():
            if value is None:
                continue

            previous = self.recent_vitals.get(vital)
            baseline = self.baseline.get(vital)
            jump_limit = self.jump_limits.get(vital)
            change_limit = self.change_limits.get(vital)

            if (
                jump_limit is None
                or change_limit is None
                or previous is None
                or baseline is None
            ):
                continue

            jump = abs(value - previous)
            change_alert = f"{vital}_sudden_change"

            if not self.sudden_change_active[vital]:
                if jump >= jump_limit:
                    self.sudden_change_active[vital] = True
                    self.change_counters[vital] = 1
            else:
                difference = abs(value - baseline)
                if difference >= change_limit:
                    self.change_counters[vital] += 1
                else:
                    # Returned to baseline range: reset counters & re-arm change alert
                    self.change_counters[vital] = 0
                    self.sudden_change_active[vital] = False
                    self.activeConditions.pop(change_alert, None)
                    self.activeAlerts.pop(change_alert, None)
                    self.resolvedConditions.pop(change_alert, None)

            if self.change_counters[vital] == self.required_readings:
                self.generate_alert(
                    change_alert,
                    vital,
                    value,
                    f"{vital.upper()} showed a sudden persistent change",
                )

    def receive_reading(self, bpm, temperature, spo2):
        new_reading = {"bpm": bpm, "temperature": temperature, "spo2": spo2}
        self.check_changes(new_reading)
        self.readingHistory.append(new_reading)
        self.recent_vitals = new_reading.copy()
        self.checkThresholds()

    def generate_alert(self, alert_type, vital, reading, reason):
        # Block alert generation if active OR if suppressed pending return to normal range
        if (
            alert_type in self.activeConditions
            or alert_type in self.resolvedConditions
        ):
            return

        self.activeConditions[alert_type] = True
        alert = {
            "patient_id": self.patientId,
            "alert_type": alert_type,
            "vital": vital,
            "reading": reading,
            "reason": reason,
        }

        self.activeAlerts[alert_type] = alert
        if self.alert_callback:
            self.alert_callback(alert)

    def resolve_alert(self, alert_type):
        """Removes alert from active status and latches it until vitals return to normal range."""
        self.activeAlerts.pop(alert_type, None)
        self.activeConditions.pop(alert_type, None)
        self.resolvedConditions[alert_type] = True

    def reset_all_alerts(self):
        """Suppresses all active alerts until vitals recover back inside normal threshold bounds."""
        for alert_type in list(self.activeAlerts.keys()):
            self.resolve_alert(alert_type)
        for alert_type in list(self.activeConditions.keys()):
            self.resolve_alert(alert_type)