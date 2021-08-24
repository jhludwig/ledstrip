# led-strip
An agent to listen to iotbox MQTT commands and control an LED strip.  

Requires an RPI and a neopixel LED strip.  Inspiration: https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage, https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring

# Why

zigbee/zwave lights are great but are power hungry and bulky.  If you want to put 10 lights on bookshelf, that is a lot of cabling and fixures.  an led strip that is pixel addressable would take far less room and power.

# Usage

    sudo su                              # unfortunately pi led stuff has to run as root
    pip install -r requirements.txt      # install requirements -- first time only
    # run the app.  the IOT_DEVICE_NAME should be unique, will be used to address the node in the game
    export $(grep -v '^#' iotgame.env | xargs) && IOT_DEVICE_NAME=bookshelfstrip python3 iotbox_led.py

Then in a second terminal window

    mqtt pub -t iotbox/jhludwig/bookshelfstrip/LEDSTRIP -m "highlight 0,128,0,0 .5,0,255,0"
    mqtt pub -t iotbox/jhludwig/bookshelfstrip/LEDSTRIP -m "fade 0,45,45,0 .5,0,0,128"
    mqtt pub -t iotbox/jhludwig/bookshelfstrip/LEDSTRIP -m "clear"

# Notes

- "clear" or "stop" commands are immediate, all values wiped 
- "highlight" is immediate, new values instantly lighted.  highlight is destructive, any old values are forgotten
- "fade" has same ultimate effect as highlight, but crossfades from current state to new state over 2 seconds.  it is destructive, the old state is fogotten.  
  