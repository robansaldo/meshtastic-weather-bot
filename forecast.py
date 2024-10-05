import json, re, time, datetime, html, requests, textwrap
import paho.mqtt.client as mqtt

broker  = "yourmqttserver"
user    = "yourmqttuser"
password = "yourmqttpassword"
port    = 1883
client_id = "mesh-weather-listener"
topic   = "msh/2/json/mqtt/" # this topic is necessary for the node to receive the message
useragent = "YOURUA" # NWS would like user-agent to be something they can contact you with
wxurl = "URLFORFORECAST" # eg; https://api.weather.gov/gridpoints/BOX/19,85/forecast

# id of sending node
bot = YOURDECIMALNODEID # eg; 12345678

# interval between messages
sleep = 15
# maximum per message length
maxlength = 120

# debugging
def xalert(text):
    print(text)

def alert(text):
    client = mqtt.Client()
    client.username_pw_set(user, password)
    client.connect(broker, port, 60)
    print(text)
    message = {"from":bot,"channel":0,"type":"sendtext","payload":text}
    client.publish(topic, json.dumps(message))

def run():
    headers = {'user-agent': useragent}
    # Forecast URL for the center of our converage area
    r = requests.get(wxurl, headers=headers)
    # if we didn't get the weather, retry once in 5 seconds
    if r.status_code != 200:
        time.sleep(5)
        r = requests.get(wxurl, headers=headers)

    data = r.json()
    if 'properties' in data:
        forecast = "Today\'s NWS weather forecast:\n" + data['properties']['periods'][1]['detailedForecast']
        lines = textwrap.wrap(forecast.replace('\n', ' '), width=maxlength)
        wl = len(lines)
        # if just one message skip numbering each message
        if wl < 2:
            alert(forecast)
        else:
            n = 0
            for l in lines:
                n += 1
                alert("(%s/%s) %s" % (n, wl, l))
                time.sleep(sleep)

if __name__ == '__main__':
    run()
