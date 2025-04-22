#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "time.h"
#include "base64.h"

// Configuración de WiFi
const char* ssid = "iPhone de Anita";
const char* password = "conectate8080";

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

// Configuración de la cámara para ESP32-CAM (AI-Thinker)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

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
    // Configurar la cámara
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Configuración de resolución
    config.frame_size = FRAMESIZE_QVGA; // 320x240
    config.jpeg_quality = 1000; // Calidad de la imagen
    config.fb_count = 1;

    if (esp_camera_init(&config) != ESP_OK) {
        Serial.println("Error al iniciar la cámara");
        return;
    }

    Serial.println("Cámara iniciada. Capturando imágenes...");
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();

    static unsigned long lastMsg = 0;
    if (millis() - lastMsg > 1000) {
        lastMsg = millis();

        DynamicJsonDocument doc(20000);

        // Obtener la marca de tiempo
        struct tm timeinfo;
        if (!getLocalTime(&timeinfo)) {
            Serial.println("Error obteniendo tiempo");
        } else {
            char timeStringBuff[50];
            strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%d %H:%M:%S", &timeinfo);
            doc["timestamp"] = timeStringBuff;
        }

        // Geolocalización ficticia (cambiar si tienes datos reales)
        doc["geolocalizacion"]["latitud"] = random(-9000, 9000) / 100.0;
        doc["geolocalizacion"]["longitud"] = random(-18000, 18000) / 100.0;

        // Capturar imagen
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            Serial.println("Error al capturar la imagen.");
            return;
        }

        // Convertir la imagen a base64
        String imageBase64 = "";
        for (size_t i = 0; i < fb->len; i++) {
            char buf[3];
            sprintf(buf, "%02X", fb->buf[i]);
            imageBase64 += buf;
        }

        esp_camera_fb_return(fb); // Liberar memoria de la imagen

        doc["imagen"] = imageBase64;

        String output;
        serializeJson(doc, output);

        Serial.println("Datos a enviar:");
        Serial.println(output);

        if (client.publish(mqtt_topic, output.c_str())) {
            Serial.println("Mensaje publicado con éxito");
        } else {
            Serial.print("Error al publicar el mensaje. Estado del cliente: ");
            Serial.println(client.state());
        }
    }

    delay(1000);
}
