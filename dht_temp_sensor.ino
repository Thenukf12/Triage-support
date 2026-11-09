#include "DHT.h"

#define DHTPIN 14     
#define DHTTYPE DHT11   

DHT dht(DHTPIN, DHTTYPE);

void setupDHT() {
  dht.begin();
  Serial.println("initializing DHT sensor");
}


void takeTemperature(float &temp) {
  temp = dht.readTemperature();
  
  if (isnan(temp)) {
    Serial.println("No temperature readings");
  }
  else{
    Serial.printf("Temperature: %.1f C\n", temp);
  }
}
