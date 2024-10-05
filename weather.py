import json, re, time, datetime, html, requests, textwrap
import paho.mqtt.client as mqtt
import sqlite3

broker  = "YOURMQTTSERVER"
user    = "MQTTUSER"
password = "MQTTPASS"
port    = 1883
client_id = "mesh-weather-listener"
topic   = "msh/2/json/mqtt/"

# the sqlite db is used to keep track of the wx alerts that have already been sent - you will need to create this db, replace with the location of your db
database = "/opt/mesh/meshtastic.db"
connection = sqlite3.connect(database)
cursor = connection.cursor()

# coverage area to search - replace with the area for your alerts
url = "https://api.weather.gov/alerts/active?area=MA"

# id of sending node - replace with the decimal id of your sending node
bot = 123456789

# maximum message length
maxlength = 150

# filter out just the zones we are interested in, replace these with the forecast zones for your area
zones = {
        'https://api.weather.gov/zones/forecast/MAZ002':'Western Franklin',
        'https://api.weather.gov/zones/forecast/MAZ003':'Eastern Franklin',
        'https://api.weather.gov/zones/forecast/MAZ010':'Eastern Hampshire',
        'https://api.weather.gov/zones/forecast/MAZ008':'Western Hampshire',
        'https://api.weather.gov/zones/forecast/MAZ011':'Eastern Hampden',
        'https://api.weather.gov/zones/forecast/MAZ009':'Western Hampden',
        'https://api.weather.gov/zones/county/MAC011':'Franklin',
        'https://api.weather.gov/zones/county/MAC015':'Hampshire',
        'https://api.weather.gov/zones/county/MAC013':'Hampden'
        }

debug = False

def alert(channel, text):
    if debug:
        print(f"channel {channel} text: {text}")
    else:
        client = mqtt.Client()
        client.username_pw_set(user, password)
        client.connect(broker, port, 60)
        print(text)
        message = {"from":bot,"channel":channel,"type":"sendtext","payload":text}
        client.publish(topic, json.dumps(message))

def run():
    headers = {'user-agent': 'pvmesh.org weather alert'}
    # get alert data from nws
    r = requests.get(url, headers=headers)
    data = r.json()
    # loop over the wx events
    for e in data['features']:
        props = e['properties']
        # by default, send to p v open channel, but under some conditions send to 0/LongFast
        channel = 4 # p v open
        if ((props['severity'] == 'Extreme' or props['severity'] == 'Severe') and (props['certainty'] == 'Observed' or props['certainty'] == 'Likely')):
            channel = 0 # longfast
        # we don't want to send the event multiple time, so get the event id and track which events we've already alerted on
        eid = props['id']
        m = cursor.execute("SELECT count(id) FROM wxevents WHERE id='" + eid + "'")
        c = m.fetchone()[0]
        # assume we're not sending it, switch to True if it hasn't been sent and meets conditions
        display = False
        if c < 1 or debug:
            # not already sent so check if it is a zone we're interested in
            for z in props['affectedZones']:
                if z in zones:
                    display = True
            if debug:
                display = True
            if display:
                if not debug:
                    # log that we're sending this one
                    cursor.execute("INSERT INTO wxevents (id) VALUES ('" + eid + "')") 
                lines = textwrap.wrap(props['description'].replace('\n', ' '), width=maxlength)
                alert(channel, props['headline'])
                num = len(lines)
                n = 0
                if not debug:
                    time.sleep(15)
                for l in lines:
                    n += 1
                    z = '(' + str(n) + '/' + str(num) + ') '
                    alert(channel, z + l)
                    if not debug:
                        time.sleep(15)
                connection.commit()

if __name__ == '__main__':
    run()
