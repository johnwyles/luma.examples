#!/usr/bin/env python3

import json
import logging
import psutil
import socket
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
SLEEP_INTERVAL = 1

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    logging.info('Connecting: {} : {}'.format(HOST, PORT))
    s.connect((HOST, PORT))

    while True:
        percentages = psutil.cpu_percent(interval=None, percpu=True)
        data = json.dumps(percentages)
        s.sendall(data.encode('utf-8'))
        data = s.recv(1024).decode('utf-8')

        if data != 'OK':
            logging.error('Not OK')
            break

        time.sleep(SLEEP_INTERVAL)

print("Received", repr(data))

