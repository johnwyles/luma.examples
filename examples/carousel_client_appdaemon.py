import appdaemon.plugins.hass.hassapi as hass
import json
import logging
import netifaces
import psutil
import socket
import time

SERVER_HOST = "192.168.1.9"  # The server's hostname or IP address
SERVER_PORT = 65432  # The port used by the server
SLEEP_INTERVAL = 0.5


class Carousel(hass.Hass):

    def initialize(self):
        logging.basicConfig(level=logging.INFO)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            logging.info('Connecting: {} : {}'.format(SERVER_HOST, SERVER_PORT))
            s.connect((SERVER_HOST, SERVER_PORT))

            while True:
                logging.info("Getting system data...")

                # CPU
                cpu_percent = psutil.cpu_percent(interval=None, percpu=False)
                cpu_percent_each = psutil.cpu_percent(interval=None, percpu=True)

                # Memory
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                mem_used_pct = (mem.total - mem.available) * 100.0 / mem.total

                # Disk
                df = psutil.disk_usage("/")

                # Network
                address = "Unknown"
                bytes_recv = 0
                bytes_sent = 0
                counters = []
                interface_name = "unknown"
                default_gw = netifaces.gateways()['default'][netifaces.AF_INET]
                ip_address = netifaces.ifaddresses(default_gw[1])[netifaces.AF_INET][0]['addr']
                if "eth0" in psutil.net_if_addrs():
                    interface_name = "eth0"
                    interface_address = psutil.net_if_addrs()["eth0"][0].address
                    bytes_recv = psutil.net_io_counters(pernic=True)["eth0"].bytes_recv
                    bytes_sent = psutil.net_io_counters(pernic=True)["eth0"].bytes_sent
                elif "wlan0" in psutil.net_if_addrs():
                    interface_name = "wlan0"
                    interface_address = psutil.net_if_addrs()["wlan0"][0].address
                    bytes_recv = psutil.net_io_counters(pernic=True)["wlan0"].bytes_recv
                    bytes_sent = psutil.net_io_counters(pernic=True)["wlan0"].bytes_sent
                elif "en0" in psutil.net_if_addrs():
                    interface_name = "en0"
                    interface_address = psutil.net_if_addrs()["en0"][0].address
                    bytes_recv = psutil.net_io_counters(pernic=True)["en0"].bytes_recv
                    bytes_sent = psutil.net_io_counters(pernic=True)["en0"].bytes_sent

                # Battery
                battery_pct = ""
                try:
                    battery_pct = psutil.sensors_battery().percent
                except:
                    battery_pct = "100"

                # Build the payload
                send_data = {
                    "cpu": {
                        "cpu_percent": cpu_percent,
                        "cpu_percent_each": cpu_percent_each
                    },
                    "disk": {
                        "free": df.free,
                        "total": df.total,
                        "used_pct": (df.total - df.free) / df.free * 100
                    },
                    "memory": {
                        "mem_used": mem.used,
                        "swap_used": swap.used,
                        "mem_used_pct": mem_used_pct,
                    },
                    "network": {
                        "ip_address": ip_address,
                        "interface_name": interface_name,
                        "interface_address": interface_address,
                        "bytes_recv": bytes_recv,
                        "bytes_sent": bytes_sent
                    },
                    "battery": {
                        "battery_pct": battery_pct
                    }
                }

                # Convert to JSON and send
                data = json.dumps(send_data)
                logging.info('Sending JSON system data: {}'.format(data))
                s.sendall(data.encode('utf-8'))
                logging.info('Waiting for OK...')

                # Acknowledged
                data = s.recv(1024).decode('utf-8')
                if data != 'OK':
                    logging.error('Not OK.')
                    break
                logging.info('Received OK.')

                # Wait
                time.sleep(SLEEP_INTERVAL)

        print("Received", repr(data))
