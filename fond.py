#!/usr/bin/env python3

# Uses Copernicus Climate Change Service information 2020
# (as per their license ?)

# This requires a valid ~/.cdsapirc
# See <https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-europe-air-quality-forecasts?tab=form>

import sys
import functools
from datetime import datetime, timedelta

import cdsapi
import pygrib

# We define MintData as an array of [datetime, c(NO2), c(O3), c(PM10), c(PM2.5)]
# Concentrations are in µg/m3 and datetime in UTC

# We assume the data we receive is ordered by time, and the measured parameter is in order: NO2, O3, PM10, PM2.5

# Download forecast data from midnight until upto hours for [NO2, O3, PM10, PM2.5]
# Returns the filename of the downloaded file.
def download_grib_from_cams (date, area, upto = 6, filename = None):
    
    date_s = date.strftime('%Y-%m-%d')

    if filename is None:
        filename = f"{date_s}.grib"

    request = {
        'model': 'chimere',
        'date': f"{date_s}/{date_s}",
        'format': 'grib',
        'type': 'forecast',
        'time': '00:00',
        'variable': [
            # NB order matters
            'nitrogen_dioxide', 'ozone', 'particulate_matter_10um',
            'particulate_matter_2.5um',
        ],
        'level': '0',
        'leadtime_hour': [ str(i) for i in range(upto+1) ],
        'area': area,
    }

    c = cdsapi.Client()
    c.retrieve('cams-europe-air-quality-forecasts', request, filename)

    return filename

# Extract MintData from the cams pygrib.open object and convert to sirane units
def extract_cams_data (data, lat1, lat2, lon1, lon2):
    r = []

    chunk_index = 0 # If we creates chunks of 4, index in that chunk
    for grib in data:
        if chunk_index == 0:
            dt = datetime(grib.year, grib.month, grib.day, grib.hour, grib.minute, grib.second)
            dt += timedelta(hours = grib.forecastTime)
            data_pollu = []

        (data, lats, lons) = grib.data(lat1=lat1, lat2=lat2, lon1=lon1, lon2=lon2)
        if data.shape == (1, 1):
            # We grabbed the single datapoint !
            p = data[0, 0]
            p = p * 1e9 # Convert kg/m3 to µg/m3
            data_pollu.append(p)
        else:
            raise Exception("Multiple points in grib selection")

        chunk_index += 1
        if chunk_index == 4:
            chunk_index = 0

            r.append([dt, *data_pollu])
    
    return r

# Takes a MintData and prints sirane input data
def print_sirane_fond_input (data, file = sys.stdout):
    # Define a print function to use our defaults
    p = functools.partial(print, sep = "\t", file = file)

    # Print header
    p('Date', 'NO2', 'O3', 'PM10', 'PM2.5')

    for d in data:
        # Format to DD/MM/YYYY HH:MM
        date = d[0].strftime("%d/%m/%Y %H:%M")

        p(date, *d[1:])

GRIB_RESOLUTION = 0.1

# NB hope that your square doesn't happen to overlap with the 0 meridian as it will not work properly
NANTES_COORD = [47.2172500, -1.5533600 + 360]
NANTES_LAT1 = NANTES_COORD[0] - GRIB_RESOLUTION / 2
NANTES_LAT2 = NANTES_COORD[0] + GRIB_RESOLUTION / 2
NANTES_LON1 = NANTES_COORD[1] - GRIB_RESOLUTION / 2
NANTES_LON2 = NANTES_COORD[1] + GRIB_RESOLUTION / 2

# Upper left, Lower right
area = [
    NANTES_COORD[0] + GRIB_RESOLUTION,
    NANTES_COORD[1] - GRIB_RESOLUTION - 360,
    NANTES_COORD[0] - GRIB_RESOLUTION,
    NANTES_COORD[1] + GRIB_RESOLUTION - 360,
]

# Downloads and prints CAMS 6 hour (modifiable) pollutant forecast data in sirane format
grib_filename = download_grib_from_cams(datetime.utcnow(), area)
data = pygrib.open(grib_filename)
data = extract_cams_data(data, NANTES_LAT1, NANTES_LAT2, NANTES_LON1, NANTES_LON2)
print_sirane_fond_input(data)
