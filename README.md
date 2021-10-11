# led-strip
A raspberry pi agent to listen to MQTT commands and control an LED strip.  

Requires an RPI and a neopixel LED strip.  Inspiration: 

- https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
- https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring

# Why

I wanted addressable lights on my bookshelf to highlight different books/items/art on the bookshelf at different times.  A pixel addressable led strip is power and space efficient.

# Usage

On the PI, first install the neopixel drivers as per https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage

Then:

    git clone git@github.com:jhludwig/ledstrip.git
    sudo su                                             # unfortunately pi led driver has to run as root
    pip install -r requirements.txt                     # install requirements -- first time only

Edit the ledstrip.env to have the MQTT credentials for your broker.  then run the app.  the LED_DEVICE_NAME should be unique, will be used to address the node

    export $(grep -v '^#' ledstrip.env | xargs) && LED_DEVICE_NAME=bookshelfstrip python3 ledstrip.py

The LED strip is modelled as a continuous element from -1 to 1, with each point able to take on a GRB value.  Any point in the range can be illuminated, with a nice gaussian spread of intensity around that point.

On any device with the MQTT CLI installed (https://hivemq.github.io/mqtt-cli/), you can issue commands

    # HIGHLIGHT a single point at .1 with the GRB values of 128, 0, 0.  highlight will take place immediately 
    # and existing light # state will be wiped
    mqtt pub -t ledstrip/bookshelfstrip/LEDSTRIP -m "highlight .1,128,0,0"
    # HIGHLIGHT multiple points with different GRB values
    mqtt pub -t ledstrip/bookshelfstrip/LEDSTRIP -m "highlight 0,128,0,0 .5,0,255,0"

    # FADE to a new set of highlighted points from the current state.  
    mqtt pub -t ledstrip/bookshelfstrip/LEDSTRIP -m "fade 0,45,45,0 .5,0,0,128"

    # SPARKLE -- randomly sparkle all the LEDS with a given color for a period of time
    mqtt pub -t ledstrip/bookshelfstrip/LEDSTRIP -m "sparkle 128,64,192"

    # the following are all synonyms, all LEDs are immediately turned off
    mqtt pub -t ledstrip/bookshelfstrip/LEDSTRIP -m "clear"
    mqtt pub -t ledstrip/bookshelfstrip/LEDSTRIP -m "stop"
    mqtt pub -t ledstrip/bookshelfstrip/LEDSTRIP -m "off"

You can have as many of these strips on a single MQTT broker as you want, just by having different LED_DEVICE_NAMEs.


  