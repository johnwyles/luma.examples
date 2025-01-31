#!/usr/bin/env python3

import json
import logging
import psutil
import socket
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
SLEEP_INTERVAL = 0.5

logging.basicConfig(level=logging.INFO)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    logging.info('Connecting: {} : {}'.format(HOST, PORT))
    s.connect((HOST, PORT))

    while True:
        logging.info("Getting system data...")
        cpu = psutil.cpu_percent(interval=None, percpu=True)

        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        mem_used_pct = (mem.total - mem.available) * 100.0 / mem.total

        df = psutil.disk_usage("/")

        address = "Unknown"
        bytes_recv = 0
        bytes_sent = 0
        counters = []
        if "wlan0" in psutil.net_if_addrs():
            address = psutil.net_if_addrs()["wlan0"][0].address
            bytes_recv = psutil.net_io_counters(pernic=True)["wlan0"].bytes_recv
            bytes_sent = psutil.net_io_counters(pernic=True)["wlan0"].bytes_sent
        elif "en0" in psutil.net_if_addrs():
            address = psutil.net_if_addrs()["en0"][0].address
            bytes_recv = psutil.net_io_counters(pernic=True)["en0"].bytes_recv
            bytes_sent = psutil.net_io_counters(pernic=True)["en0"].bytes_sent

        send_data = {
            "cpu": cpu,
            "disk": {
                "free": df.free,
                "total": df.total,
                "used": df.used,
                "used_pct": 100 - ((df.free / df.total) * 100)
            },
            "memory": {
                "mem_used": mem.used,
                "mem_used_pct": mem_used_pct,
                "swap_used": swap.used
            },
            "network": {
                "address": address,
                "bytes_recv": bytes_recv,
                "bytes_sent": bytes_sent
            }
        }

        data = json.dumps(send_data)

        logging.info('Sending JSON system data: {}'.format(data))
        s.sendall(data.encode('utf-8'))
        logging.info('Waiting for OK...')

        data = s.recv(1024).decode('utf-8')
        if data != 'OK':
            logging.error('Not OK.')
            break
        logging.info('Received OK.')

        time.sleep(SLEEP_INTERVAL)

print("Received", repr(data))
