import base64
from pymongo import MongoClient
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import json

# Clave AES base64 (debe ser de 32 bytes una vez decodificada = AES-256)
key_b64 = "MGHelL43s4+xlJW8ItxLpjYq1t1i9qOozVrblfjzg4c="
key = base64.b64decode(key_b64)

# Función para descifrar un campo
def decrypt_field(encrypted_b64: str) -> str:
    encrypted_data = base64.b64decode(encrypted_b64)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Quitar el padding
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext.decode('utf-8')

# Conexión MongoDB
MONGO_USER = "sentryuser"
MONGO_PASSWORD = "sentrypasswd"
MONGO_HOST = "195.235.211.197"
MONGO_PORT = "27170"
DB_NAME = "SENTRY"
COLLECTION_NAME = "cam2"
MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource=SENTRY"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Leer y descifrar los datos
for doc in collection.find().limit(5):  # Puedes quitar el limit si quieres todos

    try:
        geolocalizacion = decrypt_field(doc["geolocalizacion"])
        imagen = decrypt_field(doc["imagen"])
        timestamp = decrypt_field(doc["timestamp"])

        print("\nDatos descifrados:")
        print("Geolocalizacion:", json.loads(geolocalizacion))
        print("Imagen:", imagen)  
        print("Timestamp:", timestamp)
        print("-" * 80)

    except Exception as e:
        print("Error al descifrar:", e)
