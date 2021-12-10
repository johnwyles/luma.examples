#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import socket
import struct  # Needed to unpack data from UDP data packets coming from Project Cars

import board  # Access Matrix Portal
import busio  # Access SPI
import displayio  # Base class for dislaying text and graphics on the LED Matrix
from adafruit_bitmap_font import \
    bitmap_font  # Used to import fonts for display in Labels
from adafruit_display_text import label  # Used to create labels for display
from adafruit_esp32spi import \
    adafruit_esp32spi  # Also Used to set up the ESP32 Chip for connecting to WiFi
from adafruit_matrixportal.matrix import \
    Matrix  # Used in initializing the display
from digitalio import \
    DigitalInOut  # Used to set up the ESP32 Chip for connecting to WiFi


# We will use this function to set multiple attributes on a Label object at one time
# This prevents screen flicker when needing to change two things like
# label text and position
def setattrs(_self, **kwargs):
    for k, v in kwargs.items():
        setattr(_self, k, v)


# Initialize the display
MATRIX = Matrix(bit_depth=6)
display = MATRIX.display

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

logging.basicConfig(level=logging.INFO)

input_data = {}


def main():
    global input_data

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()

            with conn:
                logging.info('Connection from address ({}).'.format(addr))
                while True:
                    data = conn.recv(1024).decode('utf-8')

                    logging.info('Incoming data: ({}) bytes.'.format(len(data)))
                    try:
                        input_data = json.loads(data)
                        logging.info('Got JSON data: {}'.format(input_data))
                    except:
                        logging.error('Unable to process incoming data as JSON.')
                        break

                    try:
                        logging.info('Sending OK.')
                        conn.sendall('OK'.encode('utf-8'))
                    except:
                        logging.error('Unable to send OK.')
                        break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
