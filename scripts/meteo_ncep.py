#!/usr/bin/env python3

import sys
from sys import exit
import argparse
import functools
from math import *
from datetime import datetime

import pygrib

GRIB_RESOLUTION = 0.25

# NB hope that your square doesn't happen to overlap with the 0 meridian as it will not work properly
NANTES_COORD = [47.2172500, -1.5533600 + 360]
NANTES_LAT1 = NANTES_COORD[0] - GRIB_RESOLUTION / 2
NANTES_LAT2 = NANTES_COORD[0] + GRIB_RESOLUTION / 2
NANTES_LON1 = NANTES_COORD[1] - GRIB_RESOLUTION / 2
NANTES_LON2 = NANTES_COORD[1] + GRIB_RESOLUTION / 2

# === Conversion functions ===

# ncep[t, u, v, tcc, precip] -> sirane[wind, winddir, temp, cld, precip]
def ncep_to_sirane(data):
	r = [0] * 5

	r[0], r[1] = uv_to_sirane_udir(data[1], data[2])
	r[2] = data[0]
	r[3] = cloud_pct_to_sirane_oktas(data[3])
	r[4] = precip_to_sirane_mm_h(data[4])

	return r

# Wind: (u [m/s], v [m/s]) -> (windspeed [sirane m/s], sirane [sirane °])
def uv_to_sirane_udir (u, v):
	speed = min(30, sqrt(u*u + v*v))
	if speed <= 0:
		dir = 0
	else:
		dir = degrees(atan2(u, v))
		if dir <= 0:
			dir += 360

	return speed, dir

# Cloud cover: [%] -> [sirane oktas]
def cloud_pct_to_sirane_oktas (cc):
	return min(8, max(0, cc / 100 * 8))

# Temperature: [K] -> [sirane C]
def kelvin_to_sirane_degC (k):
	return min(50, max(-50, k - 273.15))

# Precipitation rate: [kg/m2/s] -> [sirane mm/h]
def precip_to_sirane_mm_h (p):
	return p * 3600

# === Input and output ===

def print_sirane_meteo_input (data, file = sys.stdout):
	"""
	Data is an array of [date, u, dir, temp, cld, precip] with the right types of [datetime, float, float, float, float, float]
	"""
	# Define a print function to use our defaults
	p = functools.partial(print, sep = "\t", file = file)

	# Print header
	p('Date', 'U', 'Dir', 'Temp', 'Cld', 'Precip')

	for d in data:
		# Format to DD/MM/YYYY HH:MM
		date = d[0].strftime("%d/%m/%Y %H:%M")

		p(date, *d[1:])

def get_datapoint (gribs, lat1, lat2, lon1, lon2):
	# Accept scalars and lists
	if isinstance(gribs, pygrib.gribmessage):
		gribs = [gribs]
	
	r = []
	for g in gribs:
		# Get data
		(data, lats, longs) = g.data(lat1=lat1, lat2=lat2, lon1=lon1, lon2=lon2)
		if data.shape == (1, 1):
			# We grabbed the single datapoint !
			r.append(data[0, 0])
		else:
			raise Exception("Multiple points in grib selection")
	return r

# Returns the single element of the array, or panics
def get_single (a):
	if len(a) != 1:
		raise Exception("Not a single element array")
	return a[0]

def display_grib_keys (g):
	for k in g.keys():
		print(f"{k} = {getattr(g, k)}")

def get_ncep_gribs (data, forecastTime):
	gribs = []
	gribs.append(get_single(data.select( forecastTime = forecastTime, shortName = 't', typeOfLevel = 'surface', level = 0 )))
	gribs.append(get_single(data.select( forecastTime = forecastTime, shortName = '10u' )))
	gribs.append(get_single(data.select( forecastTime = forecastTime, shortName = '10v' )))
	gribs.append(get_single(data.select( forecastTime = forecastTime, shortName = 'tcc', nameOfFirstFixedSurface = 'Convective cloud layer' )))
	gribs.append(get_single(data.select( forecastTime = forecastTime, shortName = 'prate' )))
	return gribs




# Récupération des arguments
parser = argparse.ArgumentParser()
parser.add_argument("grib_file")
args = parser.parse_args();

# Lecture du fichier
grib_filename = args.grib_file
data = pygrib.open(grib_filename)

forecastTime = 6 # FIXME hardcoded
print(f"Forecast time is {forecastTime}")

# Choix des données voulues
gribs = get_ncep_gribs(data, forecastTime)

# Récupération du point de données
datapoint = get_datapoint(gribs, NANTES_LAT1, NANTES_LAT2, NANTES_LON1, NANTES_LON2)
datapoint = ncep_to_sirane(datapoint)

# TODO add date

# Transformation des données

data = [ [ datetime.now(), *datapoint] ]
print_sirane_meteo_input(data)
