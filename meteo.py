#!/usr/bin/env python3

# Standard libraries
import sys
import argparse
from datetime import datetime
import functools
# External libraries
import requests

# We define the internal data exchange type MintData.
# MintData := [ [datetime, float, float, float, float, float], ...] (data types)
# MintData := [ [date, windspeed, winddir, temp, cld, precip], ...] (variable names)
# 
# In other words, if the variable d is of type MintData, then d is a list,
# and for all i, d[i] is an array of form [date, windspeed, winddir, temp, cld, precip] where:
# - date is a datetime.datetime object in UTC of the weather data time
# - windspeed is the wind speed in m/s
# - winddir is the wind direction in degrees
# - temp is the temperature in Celsius
# - cld is the cloud total cover in oktas
# - precip is the precipitation rate in mm/h
# Not mentionned here are the upper and lower bounds used by sirane for certain parameters, refer to their documentation for more details

# Get weather data from OpenWeatherMap as JSON dictionary
def request_owp_data (lat, lon, api_key):
    part = "current,minutely,daily,alerts"
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={api_key}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return data

# Take the JSON from OpenWeatherMap and turn it into an object of type MintData
def extract_owp_data (data):
    r = []
    for hour in data['hourly']:
        date = datetime.utcfromtimestamp(hour['dt'])
        temp = max(-50, min(50, hour['temp'] - 273.25 )) # T in °C in [-50; 50]
        windspeed = max(0, min(30, hour['wind_speed'] )) # Windspeed in [0; 30]

        # Wind direction in degrees. 0 is no wind, 360 is north wind
        winddir = hour['wind_deg']
        if winddir == 0:
            winddir = 360
        if windspeed == 0:
            winddir = 0
        
        cld = hour['clouds'] * 8 / 100 # Convert % into oktas
        try:
            precip = hour['rain']["1h"]
        except:
            precip = 0

        item = [date, windspeed, winddir, temp, cld, precip]

        r.append(item)
    return r

# Take the object of type MintData and print it formatted for sirane to the file (by default, stdout)
def print_sirane_meteo_input (data, file = sys.stdout):
    # Define a print function to use our defaults
    p = functools.partial(print, sep = "\t", file = file)

    # Print header
    p('Date', 'U', 'Dir', 'Temp', 'Cld', 'Precip')

    for d in data:
        # Format to DD/MM/YYYY HH:MM
        date = d[0].strftime("%d/%m/%Y %H:%M")

        p(date, *d[1:])

NANTES_COORD = [47.2172500, -1.5533600]

parser = argparse.ArgumentParser()
parser.add_argument("api_key")
args = parser.parse_args();

# Prints OWM 2 day hourly forecast in sirane format
data = request_owp_data (NANTES_COORD[0], NANTES_COORD[1], args.api_key)
data = extract_owp_data(data)
print_sirane_meteo_input(data)
