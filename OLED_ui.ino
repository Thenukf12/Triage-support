#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setupOLED() {
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3D)) {
    Serial.println("FAILED: OLED not found");
    return;
  }
  Serial.println("SUCCESS: OLED found!");
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.display();
}

void updateOLED() {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);
  display.setCursor(0, 0);
  display.println("BAND-4");
  display.println("Battery");
  display.printf("98%");
  display.display();
}