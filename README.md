# meshtastic-weather-bot

A couple of simple scripts to send weather information to your meshtastic mesh. These both depend on having a node connected to a MQTT server. Using a private MQTT server is highly recommended as anyone can send a message to your network if they can publish a MQTT message. Your sending node must have a channel with the name "mqtt" with "downlink" enabled as described here: https://meshtastic.org/docs/software/integrations/mqtt/#json-downlink-to-instruct-a-node-to-send-a-message 

The forecast.py script is intended to be run by a cron job at whatever time(s) of the day you want. It will send the current forecast for the area.

The weather.py script is intended to be run periodically via cron perhaps every 15 minutes or so. It will query the NWS API for current weather alerts and send them to your mesh. To keep track of which messages havealready been sent to the mesh we use a sqlite3 database to store the event ids and check the db to see if it has already been sent or not. You'll need to create a such a db on your system at the path specified in the "database" variable. Make sure that the process running the bot has write permission to the db file. To create the db use the create statement:

CREATE TABLE wxevents(id unique);

It is recommended to run these in a Python virtual environment. You will want to adjust the "zones" variable to include just the zones covered by your mesh.
