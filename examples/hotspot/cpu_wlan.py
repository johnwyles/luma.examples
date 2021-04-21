#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import time
import psutil
from luma.core.virtual import hotspot
from hotspot.common import bytes2human, right_text, tiny_font, title_text


def vertical_bar(draw, x1, y1, x2, y2, yh):
    draw.rectangle((x1, y1) + (x2, y2), "black", "white")
    draw.rectangle((x1, yh) + (x2, y2), "white", "white")


def render(draw, width, height):
    percentages = psutil.cpu_percent(interval=None, percpu=True)

    margin = 3
    top_margin = 3
    bottom_margin = 3

    title_text(draw, top_margin, width, "Net: wlan0")
    address = psutil.net_if_addrs()["wlan0"][0].address
    counters = psutil.net_io_counters(pernic=True)["wlan0"]

    draw.text((margin, 20), text=address, font=tiny_font, fill="white")
    draw.text((margin, 30), text="Rx:", font=tiny_font, fill="white")
    draw.text((margin, 40), text="Tx:", font=tiny_font, fill="white")
    right_text(draw, 30, width, margin, text=bytes2human(counters.bytes_recv))
    right_text(draw, 40, width, margin, text=bytes2human(counters.bytes_sent))

    x = (width - draw.textsize("CPU Load")[0]) / 2
    draw.text((x, 55), text="CPU Load", fill="yellow")
    bar_height = (height - 15 - top_margin - bottom_margin) / 2
    width_cpu = width / len(percentages)
    bar_width = 0.5 * width_cpu
    bar_margin = (width_cpu - bar_width) / 2

    x = bar_margin

    for cpu in percentages:
        cpu_height = bar_height * (cpu / 100.0)
        y2 = height - bottom_margin
        vertical_bar(draw,
                     x, y2 - bar_height - 1,
                     x + bar_width, y2, y2 - cpu_height)

        x += width_cpu


#class CPU_Load(hotspot):
#
#    def __init__(self, width, height, interval):
#        super(CPU_Load, self).__init__(width, height)
#        self._interval = interval
#        self._last_updated = 0
#
#    def should_redraw(self):
#        return time.time() - self._last_updated > self._interval
#
#    def update(self, draw):
#        render(draw, self.width, self.height)
#        self._last_updated = time.time()

