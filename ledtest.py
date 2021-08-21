#!/usr/bin/env python3

############################################################################
#
#  IOTBox Tesla Mapper.  Copyright 2021 IOTBox
#
#  converts game music actions into Tesla actions
#
#
#
############################################################################

import os
import time
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
import numpy as np

import board
import neopixel

ORDER = neopixel.GRB # RGB
# PIXELCOUNT = int(os.environ['IOTPIXELS'])
PIXELCOUNT = 60
x_vals = np.linspace(-1.0, 1.0, PIXELCOUNT)

MU = 0
SIGMA = 0.25

def gaussian(x, mu=MU, sig=SIGMA):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

my_env = os.environ.copy()


pixels = neopixel.NeoPixel(
    board.D18, PIXELCOUNT, brightness=0.2, auto_write=False, pixel_order=ORDER
)
pixels.fill((0,0,0))
pixels.show()

time.sleep(1)
pixels.fill((255,0,0))
pixels.show()

time.sleep(1)
pixels.fill((0,128,0))
pixels.show()

time.sleep(1)
pixels.fill((0,0,192))
pixels.show()

time.sleep(1)
pixels.fill((0,0,0))
pixels.show()