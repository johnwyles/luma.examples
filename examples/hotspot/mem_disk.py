#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

import psutil
from hotspot.common import bytes2human, right_text, title_text, tiny_font


def render(draw, width, height):
    df = psutil.disk_usage("/")

    margin = 3

    title_text(draw, margin, width, text="Disk")
    draw.text((margin, 20), text="Used:", font=tiny_font, fill="white")
    draw.text((margin, 30), text="Free:", font=tiny_font, fill="white")
    draw.text((margin, 40), text="Total:", font=tiny_font, fill="white")

    right_text(draw, 20, width, margin, text="{0:0.1f}%".format(df.percent))
    right_text(draw, 30, width, margin, text=bytes2human(df.free, "{0:0.0f}"))
    right_text(draw, 40, width, margin, text=bytes2human(df.total, "{0:0.0f}"))

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    mem_used_pct = (mem.total - mem.available) * 100.0 / mem.total

    x = (width - draw.textsize("Memory")[0]) / 2
    draw.text((x, 55), text="Memory", fill="yellow")
    draw.text((margin, 75), text="Used:", font=tiny_font, fill="white")
    draw.text((margin, 85), text="Phys:", font=tiny_font, fill="white")
    draw.text((margin, 95), text="Swap:", font=tiny_font, fill="white")

    right_text(draw, 75, width, margin, text="{0:0.1f}%".format(mem_used_pct))
    right_text(draw, 85, width, margin, text=bytes2human(mem.used))
    right_text(draw, 95, width, margin, text=bytes2human(swap.used))
