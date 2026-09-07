# Secure IoT Data Acquisition System using ESP32-CAM

## Overview

This project implements a secure IoT data acquisition system using an ESP32-CAM, MQTT communication and MongoDB storage.

The system captures images and metadata, transmits the information through MQTT, encrypts sensitive data, and stores it in a database for later retrieval and analysis.

## Features

- Image capture using ESP32-CAM
- MQTT-based communication
- Timestamp generation with NTP
- Geolocation metadata
- AES and Fernet encryption
- MongoDB integration
- Image reconstruction from hexadecimal data

## Architecture

ESP32-CAM
    ↓
MQTT Broker
    ↓
Python Processing
    ↓
Encryption
    ↓
MongoDB


## Project Structure

### Camara
Basic ESP32 implementation that sends timestamp and geolocation data through MQTT.

### funcionacion_camaracion
ESP32-CAM implementation for image capture and data transmission.

### python
Scripts for message processing, encryption, database storage and data recovery.

### Ver_Imagen
Utilities for reconstructing image files from hexadecimal data.

## Technologies

- ESP32 / ESP32-CAM
- Python
- MQTT
- MongoDB
- AES-CBC
- Fernet
- Arduino Framework

## Academic Context

Project developed as part of the Bachelor's Degree in Computer Engineering at **Universidad Europea de Madrid**.

## Authors

- Ana Esteban González
- Andrés Ramos García
- Paula Sáenz de Santa María Díez
