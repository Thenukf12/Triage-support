#define SERVICE_UUID "e7f0c18b-4d76-486b-8510-a61597ce5d14"
#define HEART_RATE_UUID "31806ba7-3d6b-4302-bc0c-ae0f761df15b"
#define SPO2_UUID "5db163c6-fdd9-4273-b047-0c6e7c65efc3"
#define TEMP_UUID "3ba32b8f-9df9-42d4-ae2a-05b9cad5ef55"

#include <Wire.h>
#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

bool device_connection = false;

BLECharacteristic *pHeartrate = nullptr;
BLECharacteristic *pSPO2 = nullptr;
BLECharacteristic *pTemp = nullptr;

class MyESP32ServerCallbacks : public BLEServerCallbacks{
  void onConnect(BLEServer *pServer) override{
    device_connection = true;
    Serial.println("laptop connected");
    delay(100);
  }

  void onDisconnect(BLEServer *pServer) override{
    device_connection = false;
    Serial.println("nothing connected");
    BLEDevice::startAdvertising();
  }
};

void setup() {
  Serial.begin(115200);
  delay(2000);

  BLEDevice::init("MyESP32Server");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyESP32ServerCallbacks);

  BLEService *pService = pServer->createService(SERVICE_UUID);

  pHeartrate = pService->createCharacteristic(
    HEART_RATE_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  pHeartrate->addDescriptor(new BLE2902());

  pSPO2 = pService->createCharacteristic(
    SPO2_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  pSPO2->addDescriptor(new BLE2902());

  pTemp = pService -> createCharacteristic(
    TEMP_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  pTemp -> addDescriptor(new BLE2902());

  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  BLEDevice::startAdvertising();

  Wire.begin(SDA, SCL);
  setupOLED();
  setupMaxSensor();
  setupDHT();
}

void loop() {
  float spo2, bpm, temp;
  readMaxSensor(spo2, bpm);
  takeTemperature(temp);

  String hrString = String(bpm, 0);
  String spo2String = String(spo2, 0);
  String tempString = String(temp, 0);

  pHeartrate -> setValue(hrString.c_str());
  pSPO2 -> setValue(spo2String.c_str());
  pTemp -> setValue(tempString.c_str());

  if (device_connection) {
    pHeartrate -> notify();
    pSPO2 -> notify();
    pTemp -> notify();
  }

  static unsigned long lastOled = 0;
  if (lastOled == 0 || millis() - lastOled > 10000) {
    lastOled = millis();
    updateOLED();
  }

  delay(3000);
}
