#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "time.h"

// Configuración de WiFi
const char* ssid = "AndroidAP1D18";
const char* password = "onnn1087";

// Configuración MQTT
const char* mqtt_server = "195.235.211.197";
const int mqtt_port = 18840;
const char* mqtt_topic = "grupo2";

// Configuración NTP
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Dirección IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("conectado");
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      Serial.println(" intentando de nuevo en 5 segundos");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  static unsigned long lastMsg = 0;
  if (millis() - lastMsg > 1000) {
    lastMsg = millis();

    DynamicJsonDocument doc(20000);  // Aumentamos el tamaño para la imagen

    struct tm timeinfo;
    if(!getLocalTime(&timeinfo)){
      Serial.println("Error obteniendo tiempo");
    } else {
      char timeStringBuff[50];
      strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%d %H:%M:%S", &timeinfo);
      doc["timestamp"] = timeStringBuff;
    }

    doc["geolocalizacion"]["latitud"] = random(-9000, 9000) / 100.0;
    doc["geolocalizacion"]["longitud"] = random(-18000, 18000) / 100.0;

    String output;
    serializeJson(doc, output);

    Serial.println("Datos a enviar:");
    Serial.println(output);
    
    Serial.print("Intentando publicar en el topic: ");
    Serial.println(mqtt_topic);
    
    if(client.publish(mqtt_topic, output.c_str())) {
      Serial.println("Mensaje publicado con éxito");
      Serial.println(client.state());
    } else {
      Serial.print("Error al publicar el mensaje. Estado del cliente: ");
      Serial.println(client.state());
    }
  }
}