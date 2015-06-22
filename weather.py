#!/usr/bin/python2.7
# Thu Oct  4 15:19:37 EDT 2012
# CLI weather app
# uses www.wunderground.com API for weather data and Geo IP lookup
# accepts 1 zip code as argument (optional)
'''
Todo:
- average temp / history
'''
import os
import re
import sys
import json
from urllib2 import urlopen
from textwrap import wrap

# get API key
with open('api_key.txt', 'r') as f:
    api_key = f.readline().strip()
    std_url = 'http://api.wunderground.com/api/{key}/'.format(key=api_key)

try: 
    # zip code given
    zipcode = sys.argv[1] 
except IndexError: 
    # look up zip code based on maxmind geoip api
    geoip_url = std_url+ 'geolookup/q/autoip.json'
    response = json.loads(urlopen(geoip_url).read())
    zipcode = response['location']['zip']

# build URLs for API calls
alerts_url = std_url + 'alerts/q/' + zipcode + '.json'
conditions_url = std_url + 'conditions/q/' + zipcode + '.json'
forecast_url = std_url + 'forecast/q/' + zipcode + '.json'

# call API, responds with raw JSON
raw_json_conditions = urlopen(conditions_url).read()
raw_json_alerts = urlopen(alerts_url).read()
raw_json_forecast = urlopen(forecast_url).read()

# parsed JSON, acts like a dictionary
parsed_conditions = json.loads(raw_json_conditions)
parsed_alerts = json.loads(raw_json_alerts)
parsed_forecast = json.loads(raw_json_forecast)

try: 
    # attempt to find location string
    location = parsed_conditions['current_observation']['display_location']['full']
except KeyError: 
    print 'That location doesn\'t exist!'
    sys.exit()

screen_width = int(os.popen('stty size', 'r').read().split()[1]) - 12

weather = parsed_conditions['current_observation']['weather'] 
humidity = parsed_conditions['current_observation']['relative_humidity']
humidity = 'N/A' if '-' in humidity else humidity # if value is negative for some reason
wind = parsed_conditions['current_observation']['wind_string']
feels_like = parsed_conditions['current_observation']['feelslike_string']
forecast = (
    parsed_forecast['forecast']['txt_forecast']['forecastday'][1]['title'] 
    + ' - '
    + parsed_forecast['forecast']['txt_forecast']['forecastday'][1]['fcttext']
)

forecast = iter(wrap(forecast, screen_width)) 

try: # attempt to find weather alert 
    alert_message = parsed_alerts['alerts'][0]['message'] # weather alert exists
except IndexError: # alert message key doesn't exist 
    alert_message = '' # no weather alerts

print location
print '-' * len(location)
print 'Weather:   ',weather
print 'Temp:      ',feels_like
print 'Humidity:  ',humidity
print 'Winds:     ',wind

print 'Forecast:  ',next(forecast) # pop first line of forecast
for line in forecast:
    print '           ',line
if alert_message: # weather alert exists
    print '\033[91m' + '[ Alert ]' + '\033[0m',alert_message.rstrip()
print ""
