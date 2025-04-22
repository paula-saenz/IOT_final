import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Generar clave AES-256 (32 bytes) y convertir a base64 para visualización
key = base64.b64decode("MGHelL43s4+xlJW8ItxLpjYq1t1i9qOozVrblfjzg4c=")

# Configuración MQTT
MQTT_BROKER = "195.235.211.197"
MQTT_PORT = 18840
MQTT_TOPIC = "grupo2"

# Configuración MongoDB
MONGO_USER = "sentryuser"
MONGO_PASSWORD = "sentrypasswd"
MONGO_HOST = "195.235.211.197"
MONGO_PORT = "27170"
DB_NAME = "SENTRY"
COLLECTION_NAME = "cam2"

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=SENTRY"

# Función de cifrado AES-CBC con padding
def encrypt_field(data: str) -> str:
    # Convertir datos a bytes
    data_bytes = data.encode('utf-8')
    
    # Aplicar padding PKCS7 (bloques de 128 bits)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()
    
    # Generar IV aleatorio (16 bytes)
    iv = os.urandom(16)
    
    # Configurar cifrado AES-CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    # Cifrar datos
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combinar IV + texto cifrado y codificar en base64
    return base64.b64encode(iv + ciphertext).decode('utf-8')

# Conexión MongoDB
try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("Conectado a MongoDB")
except Exception as e:
    print(f"Error de conexión: {e}")

# Callback MQTT
def on_message(client, userdata, msg):
    try:
        mensaje = msg.payload.decode("utf-8")
        print(f"Mensaje recibido en {msg.topic}: {mensaje}")
        
        try:
            data = json.loads(mensaje)
        except json.JSONDecodeError:
            data = {"raw_message": mensaje}

        # Cifrar campos sensibles
        encrypted_document = {
            "geolocalizacion": encrypt_field(json.dumps(data["geolocalizacion"])),
            "imagen": encrypt_field(data["imagen"]),
            "timestamp": encrypt_field(data["timestamp"])
        }
        
        collection.insert_one(encrypted_document)
        print("Datos cifrados e insertados correctamente")
    
    except Exception as e:
        print(f"Error al procesar mensaje: {e}")

# Configurar cliente MQTT
client_mqtt = mqtt.Client()
client_mqtt.on_message = on_message

try:
    client_mqtt.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("Conectado al broker MQTT")
except Exception as e:
    print(f"Error MQTT: {e}")

client_mqtt.subscribe(MQTT_TOPIC)
client_mqtt.loop_forever()


