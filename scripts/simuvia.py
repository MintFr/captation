#!/usr/bin/env python3

# Standard libraries
import sys
import argparse
from datetime import datetime
import functools
# External libraries
import requests

# We define the internal data exchange type MintData.
# MintData := [ [datetime, float, float, float], ...] (data types)
# MintData := [ [date,      Tmin,  Tmax,    Hu], ...] (variable names)

# Get weather data from OpenWeatherMap as JSON dictionary
def request_owp_data (lat, lon, api_key):
    part = "current,minutely,hourly,alerts"
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={api_key}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return data

# Take the JSON from OpenWeatherMap and turn it into an object of type MintData
def extract_owp_data (data):
    r = []
    for day in data['daily']:
        date = datetime.utcfromtimestamp(day['dt'])
        temp_min = day['temp']['min'] - 273.25 # Tmin in °C
        temp_max = day['temp']['max'] - 273.25 # Tmax in °C
        hu = day['humidity'] # Humidity in %

        item = [date, temp_min, temp_max, hu]

        r.append(item)
    return r

# Take the object of type MintData and print it formatted for simuvia to the file (by default, stdout)
def print_simuvia_meteo_input (data, file = sys.stdout):
    # Define a print function to use our defaults
    p = functools.partial(print, sep = ",", file = file)

    # Print header
    p('Jour', 'Tmin', 'Tmax', 'Hu')

    for d in data:
        # Format to YYYY-MM-DDD
        date = d[0].strftime("%Y-%m-%d")

        p(date, *d[1:])

NANTES_COORD = [47.2172500, -1.5533600]

parser = argparse.ArgumentParser()
parser.add_argument("api_key")
args = parser.parse_args();

# Prints OWM 2 day hourly forecast in sirane format
data = request_owp_data (NANTES_COORD[0], NANTES_COORD[1], args.api_key)
data = extract_owp_data(data)
print_simuvia_meteo_input(data)
