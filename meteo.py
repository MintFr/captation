#!/usr/bin/env python3

# Standard libraries
import sys
import argparse
from datetime import datetime
import functools
# External libraries
import requests

# Get weather data from OpenWeatherMap as JSON dictionary
def request_owp_data (lat, lon, api_key):
	part = "current,minutely,daily,alerts"
	url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={part}&appid={api_key}"
	r = requests.get(url)
	r.raise_for_status()
	data = r.json()
	return data

# Take the JSON from OpenWeatherMap and turn it
# into a list of [date, windspeed, winddir, temp, cld, precip] tuples
# in the right units for sirane
def extract_owp_data (data):
	r = []
	for hour in data['hourly']:
		date = datetime.utcfromtimestamp(hour['dt'])
		temp = max(-50, min(50, hour['temp'] - 273.25 ))
		windspeed = max(0, min(30, hour['wind_speed'] ))

		winddir = hour['wind_deg']
		if winddir == 0:
			winddir = 360
		if windspeed == 0:
			winddir = 0
		
		cld = hour['clouds'] * 8 / 100
		try:
			precip = hour['rain']["1h"]
		except:
			precip = 0

		item = [date, windspeed, winddir, temp, cld, precip]

		r.append(item)
	return r

# Take the list of data of type [date: datetime, u: float, dir: float, temp: float, cld: float, precip: float]
# in the right units for sirane
# and print it formatted for sirane to the file (by default, stdout)
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

data = request_owp_data (NANTES_COORD[0], NANTES_COORD[1], args.api_key)
data = extract_owp_data(data)
print_sirane_meteo_input(data)
