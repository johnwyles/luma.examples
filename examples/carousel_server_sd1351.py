#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import socket

from demo_opts import get_device
from luma.core.virtual import viewport, snapshot, hotspot

from hotspot import mem_disk, cpu_wlan, network
from hotspot.common import bytes2human, right_text, title_text, tiny_font

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

logging.basicConfig(level=logging.INFO)

input_data = {}


def render_disk_memory_battery(draw, width, height):
    global input_data
    if not input_data:
        return

    logging.info('Rendering Disk and Memory...')
    margin = 3

    # Disk
    title_text(draw, margin, width, text="Disk")
    draw.text((margin, 15), text="Used:", font=tiny_font, fill="white")
    draw.text((margin, 25), text="Free:", font=tiny_font, fill="white")
    draw.text((margin, 35), text="Total:", font=tiny_font, fill="white")
    right_text(draw, 15, width, margin, text="{0:0.1f}%".format(input_data["disk"]["used_pct"]))
    right_text(draw, 25, width, margin, text=bytes2human(input_data["disk"]["free"], "{0:0.0f}"))
    right_text(draw, 35, width, margin, text=bytes2human(input_data["disk"]["total"], "{0:0.0f}"))

    # Memory
    x = (width - draw.textsize("Memory")[0]) / 2
    draw.text((x, 45), text="Memory", fill="yellow")
    draw.text((margin, 57), text="Used:", font=tiny_font, fill="white")
    draw.text((margin, 67), text="Phys:", font=tiny_font, fill="white")
    draw.text((margin, 77), text="Swap:", font=tiny_font, fill="white")
    right_text(draw, 57, width, margin, text="{0:0.1f}%".format(input_data["memory"]["mem_used_pct"]))
    right_text(draw, 67, width, margin, text=bytes2human(input_data["memory"]["mem_used"]))
    right_text(draw, 77, width, margin, text=bytes2human(input_data["memory"]["swap_used"]))

    # Battery
    draw.text((x, 90), text="Battery", fill="yellow")
    battery_pct = input_data["battery"]["battery_pct"]
    draw.text((margin, 105), text="{} %".format(battery_pct), font=tiny_font, fill="white")


def horizontal_bar(draw, x1, y1, x2, y2, xw):
    draw.rectangle((x1, y1) + (x2, y2), "black", "white")
    draw.rectangle((xw, y1) + (x2, y2), "white", "white")


def vertical_bar(draw, x1, y1, x2, y2, yh):
    draw.rectangle((x1, y1) + (x2, y2), "black", "white")
    draw.rectangle((x1, yh) + (x2, y2), "white", "white")


def render_network_cpu(draw, width, height):
    global input_data
    if not input_data:
        return

    logging.info('Rendering Network and CPU...')
    margin = 3
    top_margin = 3
    bottom_margin = 3

    # Network
    title_text(draw, top_margin, width, "Net: {}".format(input_data["network"]["interface_name"]))
    # interface_address = input_data["network"]["interface_address"]
    ip_address = input_data["network"]["ip_address"]
    # draw.text((margin, 15), text=interface_address, font=tiny_font, fill="white")
    draw.text((margin, 15), text=ip_address, font=tiny_font, fill="white")
    draw.text((margin, 25), text="Rx:", font=tiny_font, fill="white")
    draw.text((margin, 35), text="Tx:", font=tiny_font, fill="white")
    right_text(draw, 25, width, margin, text=bytes2human(input_data["network"]["bytes_recv"]))
    right_text(draw, 35, width, margin, text=bytes2human(input_data["network"]["bytes_sent"]))

    # CPU
    x = (width - draw.textsize("CPU Load")[0]) / 2
    draw.text((x, 45), text="CPU Load", fill="yellow")
    bar_height = (height - 15 - top_margin - bottom_margin) / 1.95
    width_cpu = width / len(input_data["cpu"]["cpu_percent_each"])
    bar_width = 0.5 * width_cpu
    bar_margin = (width_cpu - bar_width) / 1.95
    cpu_percent_string = "{}%".format(str(input_data["cpu"]["cpu_percent"]))
    x = (width - draw.textsize(cpu_percent_string)[0]) / 1.7
    draw.text((x, 57), text=cpu_percent_string, font=tiny_font, fill="white")
    x = bar_margin
    for cpu in input_data["cpu"]["cpu_percent_each"]:
        cpu_height = bar_height * (cpu / 100.0)
        y2 = height - bottom_margin
        vertical_bar(draw,
                     x, y2 - bar_height - 1,
                     x + bar_width, y2, y2 - cpu_height)
        x += width_cpu


def main():
    global device, input_data

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()

            # Setup the display
            widget_width = device.width // 2
            widget_height = device.height

            md = snapshot(widget_width, widget_height, render_disk_memory_battery, interval=2.0)
            cpuwlan = snapshot(widget_width, widget_height, render_network_cpu, interval=0.5)

            virtual = viewport(device, width=device.width, height=device.height)
            virtual.add_hotspot(cpuwlan, (0, 0))
            virtual.add_hotspot(md, (device.width // 2, 0))

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
                        device.cleanup()
                        device = get_device()
                        break

                    try:
                        logging.info('Sending OK.')
                        conn.sendall('OK'.encode('utf-8'))
                    except:
                        logging.error('Unable to send OK.')
                        device.cleanup()
                        device = get_device()
                        break

                    virtual.set_position((0, 0))


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
