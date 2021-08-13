# led-strip
An agent to listen to iotbox MQTT commands and control an LED strip.  

Requires an RPI and a neopixel LED strip.  Inspiration: https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage, https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring

# Why

zigbee/zwave lights are great but are power hungry and bulky.  If you want to put 10 lights on bookshelf, that is a lot of cabling and fixures.  an led strip that is pixel addressable would take far less room and power.

# Usage

    python3 -m venv env                  # create en env
    source env/bin/activate              # activate
    pip install -r requirements.txt      # install requirements -- first time only
    # run the app.  the IOTBOXNODENAME should be unique, will be used to address the node in the game
    export $(grep -v '^#' iotgame.env | xargs) && IOTBOXNODENAME=ludwighouseaudio python3 mqtt_media.py

Then in a second terminal window

    <!-- MEDIANODENAME=ludwighouseaudio mqtt pub -t iotbox/jhludwig/$(IOTBOXNODENAME)/AUDIO -m "play uri \"https://open.spotify.com/track/4noe32LLODXkYV5FqkTIKT?si=d73315f57cda4e37\" " -->