import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
from cryptography.fernet import Fernet  # Importar Fernet para cifrado

cipher_key = Fernet.generate_key()
cipher = Fernet(cipher_key)

#nuestra clave:
print(f"Clave de cifrado generada: {cipher_key.decode()}")

# Configuración MQTT
MQTT_BROKER = "195.235.211.197"
MQTT_PORT = 18840
MQTT_TOPIC = "grupo2"

# Configuración de MongoDB con autenticación
MONGO_USER = "sentryuser"
MONGO_PASSWORD = "sentrypasswd"
MONGO_HOST = "195.235.211.197"
MONGO_PORT = "27170"
DB_NAME = "SENTRY"
COLLECTION_NAME = "cam2"

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=SENTRY"

# Conectar a MongoDB
try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("Conectado a MongoDB")
except Exception as e:
    print(f"Error de conexión: {e}")

# Función cuando se recibe un mensaje desde MQTT
def on_message(client, userdata, msg):
    try:
        mensaje = msg.payload.decode("utf-8")  # Decodificar mensaje
        print(f"Mensaje recibido en {msg.topic}: {mensaje}")
        
        # Convertir a JSON si es posible
        try:
            data = json.loads(mensaje)
        except json.JSONDecodeError:
            data = {"raw_message": mensaje}  # Guardar como string si no es JSON

        # Insertar en MongoDB
        # Cifrar cada campo por separado
        encrypted_geolocalizacion = cipher.encrypt(json.dumps(data["geolocalizacion"]).encode("utf-8"))
        encrypted_imagen = cipher.encrypt(data["imagen"].encode("utf-8"))
        encrypted_timestamp = cipher.encrypt(data["timestamp"].encode("utf-8"))
        
        # Crear documento con los campos cifrados
        encrypted_document = {
            "geolocalizacion": encrypted_geolocalizacion.decode("utf-8"),
            "imagen": encrypted_imagen.decode("utf-8"),
            "timestamp": encrypted_timestamp.decode("utf-8")
        }
        
        # Insertar el documento cifrado en MongoDB
        collection.insert_one(encrypted_document)
        print("Mensaje cifrado e insertado en MongoDB")
    
    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")

# Configurar cliente MQTT
client_mqtt = mqtt.Client()
client_mqtt.on_message = on_message  # Asignar la función de callback

# Conectar al broker MQTT
try:
    client_mqtt.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("Conectado al broker MQTT")
except Exception as e:
    print(f"Error al conectar al broker MQTT: {e}")

# Suscribirse al topic
client_mqtt.subscribe(MQTT_TOPIC)
print(f"Suscrito al topic: {MQTT_TOPIC}")

# Iniciar loop para escuchar mensajes
client_mqtt.loop_forever()