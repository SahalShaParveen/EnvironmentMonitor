#include <DHT.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "secrets.h"

const byte DHT_PIN = 18; 
const byte DHT_TYPE = DHT11; 
DHT dht(DHT_PIN, DHT_TYPE); 

const char* topic = "test"; 

WiFiClient espClient;
PubSubClient client(espClient);


void setup_wifi() {
    delay(10);

    Serial.println();
    Serial.print("Connecting to WiFi: ");

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    }

    Serial.println("\nWiFi connected!");
    Serial.print("ESP32 IP: "); Serial.println(WiFi.localIP());
}


void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("ESP32Client")) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
    Serial.begin(115200); 
    Serial.println("DHT11 Sensor Test: "); 
    dht.begin(); 
    setup_wifi(); 
    client.setServer(mqtt_server, 1883);
}

void loop() {

    if (!client.connected()) {
        reconnect();
    }

    client.loop(); 

    float humidity = dht.readHumidity(); 
    float temperature = dht.readTemperature(); 
     
    if (isnan(humidity) || isnan(temperature)){
        Serial.println("Failed to read from DHT sensor. "); 
        delay(2000); 
        return; 
    }

    String payload = "{";
    payload += "\"temperature\":";
    payload += temperature;
    payload += ",";
    payload += "\"humidity\":";
    payload += humidity;
    payload += "}";

    Serial.print("Publishing: ");
    Serial.println(payload);

    client.publish(topic, payload.c_str());

    delay(5000);
}