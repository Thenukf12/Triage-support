#include <Wire.h>
#include "DFRobot_BloodOxygen_S.h"

#define MAX_I2C_ADDRESS 0x57
DFRobot_BloodOxygen_S_I2C maxSensor(&Wire, MAX_I2C_ADDRESS);

void setupMaxSensor() {
  Serial.println("initializing MAX30102");

  if (!maxSensor.begin()) {
    Serial.println("MAX30102 inot connected");
    while (1) delay(1000);
  }
  Serial.println("Starting measurement");
  maxSensor.sensorStartCollect();
}


void readMaxSensor(float &spo2, float &bpm){
  maxSensor.getHeartbeatSPO2();

  spo2 = maxSensor._sHeartbeatSPO2.SPO2;
  bpm = maxSensor._sHeartbeatSPO2.Heartbeat;

  if (int(bpm) <= 0){
    Serial.println("No reading avalible");
  }
  else{
    Serial.print("SPO2: ");
    Serial.print(spo2);
    Serial.print(" %\t");

    Serial.print("Heart Rate: ");
    Serial.print(bpm);
    Serial.println(" BPM");
  }

}