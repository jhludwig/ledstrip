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
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
import random
import time
import numpy as np

from asyncio_mqtt import Client, MqttError

import board
import neopixel

FADESTEPS = 20
FADETIME = 2.0
step_time = FADETIME/FADESTEPS

SPARKLESTEPS = 100

ORDER = neopixel.GRB # RGB
PIXELCOUNT = int(os.environ['IOTPIXELS'])
x_vals = np.linspace(-1.0, 1.0, PIXELCOUNT)

MU = 0
SIGMA = 0.05

def gaussian(x, mu=MU, sig=SIGMA):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

my_env = os.environ.copy()

############################################################################
#  Create Mapper Object
############################################################################

class LEDMapper:
    def __init__(self):
        # synchronous initialization
        self.pixels = neopixel.NeoPixel(
            board.D18, PIXELCOUNT, brightness=0.2, auto_write=False, pixel_order=ORDER
        )
        self.pixels.fill((0,0,0))   
        self.pixels.show()
        pass

    async def ainit(self) -> None:
        pass

    async def stop(self):
        self.pixels.fill((0,0,0))
        self.pixels.show()

    async def sparkle(self, target_arg):
        target = target_arg.split(',')
        tgrb = [int(t) for t in target]
        for s in range(SPARKLESTEPS):
            for p in range(PIXELCOUNT):
                factor = random.random()
                self.pixels[p] = (int(factor * tgrb[0]), int(factor * tgrb[1]), int(factor * tgrb[2]))
            self.pixels.show()
            await asyncio.sleep(step_time)
        self.pixels.fill((0,0,0))   
        self.pixels.show()

    async def highlight(self, highlights):
        # highlights is a list of tuples
        #   location: -1 to 1
        #   color: RGB value at peak
        self.pixels.fill((0,0,0)) 
        for highlight_string in highlights:

            highlight = highlight_string.split(',')
            y_vals = gaussian(x_vals, mu=float(highlight[0])) # calc the dist with the input location as mean

            for idx in range(PIXELCOUNT):
                y_val = y_vals[idx]
                current_pixel = self.pixels[idx]
                new_pixel_g = current_pixel[0] + int(y_val*float(highlight[1]))
                new_pixel_r = current_pixel[1] + int(y_val*float(highlight[2]))
                new_pixel_b = current_pixel[2] + int(y_val*float(highlight[3]))
                self.pixels[idx] = (new_pixel_g, new_pixel_r, new_pixel_b)

        self.pixels.show()

    async def fade(self, highlights):
        # same as hughliught but fade to new 

        # save current state and empty goal state
        original = []
        goal = []
        for idx in range(PIXELCOUNT):
            original.append(self.pixels[idx])
            goal.append((0,0,0))

        # calculate goal state
        for highlight_string in highlights:

            highlight = highlight_string.split(',')
            y_vals = gaussian(x_vals, mu=float(highlight[0])) # calc the dist with the input location as mean

            for idx in range(PIXELCOUNT):
                y_val = y_vals[idx]
                current_pixel = goal[idx]
                new_pixel_g = current_pixel[0] + int(y_val*float(highlight[1]))
                new_pixel_r = current_pixel[1] + int(y_val*float(highlight[2]))
                new_pixel_b = current_pixel[2] + int(y_val*float(highlight[3]))
                goal[idx] = (new_pixel_g, new_pixel_r, new_pixel_b)


        # now fade it in
        for step in range(FADESTEPS):
            weight = float(step + 1)/float(FADESTEPS)
            for idx in range(PIXELCOUNT):
                new_pixel_g = min(int(weight * goal[idx][0] + (1-weight) * original[idx][0]), 255)
                new_pixel_r = min(int(weight * goal[idx][1] + (1-weight) * original[idx][1]), 255)
                new_pixel_b = min(int(weight * goal[idx][2] + (1-weight) * original[idx][2]), 255)
                self.pixels[idx] = (new_pixel_g, new_pixel_r, new_pixel_b)
            self.pixels.show()
            await asyncio.sleep(step_time)

    ############################################################################
    #  Define MQTT Setup coroutine
    ############################################################################
    async def mqtt_setup(self) -> None:
        async with AsyncExitStack() as stack:
            # Keep track of the asyncio tasks that we create, so that
            # we can cancel them on exit
            tasks = set()
            stack.push_async_callback(self.cancel_tasks, tasks)

            # Connect to the MQTT broker
            self.client = Client(hostname=os.environ['MQTTHOST'], username=os.environ['MQTTUSER'], password=os.environ['MQTTPASS'])
            await stack.enter_async_context(self.client)
            print("Connected to MQTT")

            # create topic filters
            topic_filters = (
                os.path.join(os.environ['GAME_TOPIC'], os.environ['IOT_DEVICE_NAME'],"LEDSTRIP", "#"),
            )

            for topic_filter in topic_filters:
                # Handle all messages that matches the filter
                manager = self.client.filtered_messages(topic_filter)
                messages = await stack.enter_async_context(manager)
                task = asyncio.create_task(self.handle_messages(messages))
                tasks.add(task)

            # Subscribe to topic(s)
            # 🤔 Note that we subscribe *after* starting the message
            # loggers. Otherwise, we may miss retained messages.
            # await client.subscribe("iotbox/#")
            for topic_filter in topic_filters:
                await self.client.subscribe(topic_filter)
                print(f"Subscribed to {topic_filter}")

            await asyncio.gather(*tasks)

    async def run(self) -> None:
        # Run the advanced_example indefinitely. Reconnect automatically
        # if the connection is lost.
        reconnect_interval = 3  # [seconds]
        while True:
            try:
                await self.mqtt_setup()
            except MqttError as error:
                print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
            finally:
                await asyncio.sleep(reconnect_interval)

    ############################################################################
    #  Handle device messages
    ############################################################################
    async def handle_messages(self, messages) -> None:
        async for message in messages:
            
            # 🤔 Note that we assume that the message paylod is an
            # UTF8-encoded string (hence the `bytes.decode` call).
            topic = message.topic
            print(f"received topic: {topic}")
            if topic == os.path.join(os.environ['GAME_TOPIC'], os.environ['IOT_DEVICE_NAME'],"LEDSTRIP"):
                print(f"handling message: {message.topic} {message.payload.decode()}")
                payload = message.payload.decode()
                payload_list = payload.split(" ")
                if payload_list[0] in ["stop", "clear", "off"]:
                    await self.stop()
                elif payload_list[0] == "highlight":
                    await self.highlight(payload_list[1:])
                elif payload_list[0] == "fade":
                    await self.fade(payload_list[1:])
                elif payload_list[0] == "sparkle":
                    await self.sparkle(payload_list[1])
            

    ############################################################################
    #  Handle shutdown
    ############################################################################
    async def cancel_tasks(tasks) -> None:
        for task in tasks:
            if task.done():
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

############################################################################
#  MQTT loop setup
############################################################################
async def main() -> None:
    mapper = LEDMapper()
    await mapper.ainit()
    await mapper.run()

############################################################################
#  And go...
############################################################################
asyncio.run(main())