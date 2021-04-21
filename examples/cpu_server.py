#!/usr/bin/env python3

import json
import logging
import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

logging.basicConfig(level=logging.INFO)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        logging.info('Connection from address ({}).'.format(addr))
        while True:
            data = conn.recv(1024).decode('utf-8')
            # if not data:
            #     break

            logging.info('Incoming data: ({}) bytes.'.format(len(data)))
            try:
                percentages = json.loads(data)
                logging.info('Got JSON data: {}'.format(percentages))
            except:
                logging.error('Unable to process incoming data as JSON.')

            conn.sendall('OK'.encode('utf-8'))

