#!/usr/bin/env python3

# Uses Copernicus Climate Change Service information 2020
# (as per their license ?)

# This requires a valid ~/.cdsapirc
# See <https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-europe-air-quality-forecasts?tab=form>

import argparse
import configparser
import os
import sys
import functools
from datetime import datetime, timedelta

import cdsapi
import pygrib

# We define MintData as an array of [datetime, c(NO2), c(O3), c(PM10), c(PM2.5)]
# Concentrations are in µg/m3 and datetime in UTC

# We assume the entries in the grib file are grouped by 4 for each time forecast time,
# and the 4 entries are in order: NO2, O3, PM10, PM2.5
# It turns out the entry groups are not sorted by time, but alphabetically ie. 1 10 11 12 … 2 20 21 … 3 4 5 6 …


# Download forecast data from midnight until $upto hours for [NO2, O3, PM10, PM2.5]
# Returns the filename of the downloaded file.
def download_grib_from_cams (date, area, upto = None, filename = None):
    if upto is None: upto = 6

    date_s = date.strftime('%Y-%m-%d')
    if filename is None:
        filename = "fond_%s.grib" % date_s

    request = {
        'model': 'chimere',
        'date': "%s/%s" % (date_s, date_s),
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
def extract_cams_data (gribs, lat1, lat2, lon1, lon2):
    r = []

    # Loop over gribs 4 elements at a time
    gribs = iter(gribs)
    while True:
        # Consider the next 4 grib entries: NO2, O3, PM10, PM2.5
        grib_no2 = next(gribs, None)
        if grib_no2 is None: break # No more entries
        grib_o3, grib_pm10, grib_pm2_5 = next(gribs), next(gribs), next(gribs)

        # Grab timestamp
        dt = datetime(grib_no2.year, grib_no2.month, grib_no2.day, grib_no2.hour, grib_no2.minute, grib_no2.second)
        dt += timedelta(hours = grib_no2.forecastTime)

        # Fill data_pollu with a value from each grib
        data_pollu = [dt]
        for grib in [grib_no2, grib_o3, grib_pm10, grib_pm2_5]:
            (data, lats, lons) = grib.data(lat1=lat1, lat2=lat2, lon1=lon1, lon2=lon2)
            if data.shape == (1, 1):
                # We grabbed the single datapoint !
                p = data[0, 0]
                p = p * 1e9 # Convert kg/m3 to µg/m3
                data_pollu.append(p)
            else:
                raise Exception("Multiple points in grib selection")
        r.append(data_pollu)
    
    return r


# Sort MintData in ascending time, inplace
def sort_data (data):
    data.sort(key = lambda x: x[0])


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


def main(outputfile = None, configfile = None, tohour = None):
    # === Read configuration file ===

    if configfile is None:
        configfile = 'config.ini'

    config = configparser.ConfigParser()
    config.read(configfile)
    try:
        cdsapircfile = config['fond']['cdsapircfile']
    except:
        cdsapircfile = 'atmosphere.cdsapirc'
    lat, lon = config['GENERAL']['latitude'], config['GENERAL']['longitude']
    lat, lon = float(lat), float(lon)

    # === Download grib file and extract data ===

    GRIB_RESOLUTION = 0.1

    # NB hope that your square doesn't happen to overlap with the 0 meridian as it will not work properly
    lat1 = lat - GRIB_RESOLUTION / 2
    lat2 = lat + GRIB_RESOLUTION / 2
    lon1 = (lon - GRIB_RESOLUTION / 2 + 360) % 360
    lon2 = (lon + GRIB_RESOLUTION / 2 + 360) % 360

    # Upper left, Lower right
    area = [
        lat + GRIB_RESOLUTION,
        lon - GRIB_RESOLUTION,
        lat - GRIB_RESOLUTION,
        lon + GRIB_RESOLUTION,
    ]

    os.environ['CDSAPI_RC'] = cdsapircfile

    grib_filename = download_grib_from_cams(datetime.utcnow(), area, upto = tohour)
    data = pygrib.open(grib_filename)
    data = extract_cams_data(data, lat1, lat2, lon1, lon2)
    sort_data(data)
    if outputfile is not None:
        with open(outputfile, 'w') as f:
            print_sirane_fond_input(data, file = f)
    else:
        print_sirane_fond_input(data)
    os.unlink(grib_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--config")
    parser.add_argument("--tohour")
    args = parser.parse_args()

    if args.tohour is not None: args.tohour = int(args.tohour)

    main(outputfile = args.file, configfile = args.config, tohour = args.tohour)