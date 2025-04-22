import binascii

# Ruta del archivo que contiene la cadena HEX
archivo_hex = "entrada_hex.txt"
salida_imagen = "imagen_salida.jpg"

# Leer la cadena hexadecimal desde el archivo
with open(archivo_hex, "r") as archivo:
    hex_str = archivo.read()

# Limpiar la cadena (por si hay espacios o saltos de línea)
hex_str = ''.join(hex_str.split())

# Asegurar que la longitud sea par
if len(hex_str) % 2 != 0:
    raise ValueError("La cadena hexadecimal debe tener una longitud par.")

# Convertir a binario
imagen_bytes = binascii.unhexlify(hex_str)

# Guardar como imagen
with open(salida_imagen, "wb") as imagen:
    imagen.write(imagen_bytes)

print(f"✅ Imagen guardada como {salida_imagen}")
