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
import subprocess
from datetime import datetime, timedelta

import cdsapi

# We define MintData as an array of [datetime, c(NO2), c(O3), c(PM10), c(PM2.5)]
# Concentrations are in µg/m3 and datetime in UTC

# We assume the entries in the grib file are grouped by 4 for each time forecast time,
# and the 4 entries are in order: NO2, O3, PM10, PM2.5
# It turns out the entry groups are not sorted by time, but alphabetically ie. 1 10 11 12 … 2 20 21 … 3 4 5 6 …


# Download forecast data from midnight until $upto hours for [NO2, O3, PM10, PM2.5]
# Returns the filename of the downloaded file.
def download_netcdf_from_cams (date, area, upto = None, filename = None):
    if upto is None: upto = 24

    date_s = date.strftime('%Y-%m-%d')
    if filename is None:
        filename = "fond_%s.nc" % date_s

    request = {
        'model': 'ensemble', # used to be 'chimere', but it didn't work one day
        'date': "%s/%s" % (date_s, date_s),
        'format': 'netcdf',
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


# Call a java program that opens the netcdf file for us and extracts the data we want
# Then, retrieve its output and convert it to MintData
# NB the java program should output the values in the right order of NO2 O3 PM10 PM2.5
def extract_cams_data_java (java, jarname, netcdf_filename, lat, lon):
    # Call java program
    cmd = "%s -jar %s -netcdf %s -lat %s -lon %s" % (java, jarname, netcdf_filename, lat, lon)
    print("$ " + cmd, file = sys.stderr)
    p = subprocess.run(cmd, shell = True, stdout = subprocess.PIPE, universal_newlines = True)
    lines = p.stdout.split("\n")

    # The first line tells us the day
    day = datetime.strptime(lines.pop(0).split(" ")[-1], "%Y%m%d")

    # The second line lists the hours
    times = lines.pop(0).split(" ")
    _label = times.pop(0)
    data = []
    for hour_s in times:
        data.append([ day + timedelta(hours = int(float(hour_s))) ]) # Convert to float first because int() can't handle 'x.0'
    
    # The rest of the lines contain the data
    for row in lines:
        fields = row.split(" ")
        _label = fields.pop(0)
        for i, value in enumerate(fields):
            data[i].append(float(value)) # No conversion needed, already in µg/m3
    
    return data


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


def main(outputfile = None, configfile = None, tohour = None, keepgrib = False, java = None, jar = None):
    # === Read configuration file ===

    if configfile is None:
        configfile = 'config.ini'

    # Read configuration
    config = configparser.ConfigParser()
    config.read(configfile)
    try:
        cdsapircfile = config['fond']['cdsapircfile']
    except:
        cdsapircfile = 'atmosphere.cdsapirc'
    lat, lon = config['GENERAL']['latitude'], config['GENERAL']['longitude']
    lat, lon = float(lat), float(lon)
    if java is None:
        try:
            java = config['fond']['java11']
        except:
            java = 'java'
    if jar is None:
        try:
            jar = config['fond']['fond_jar']
        except:
            jar = "fond_extract_data-all.jar"

    # === Download grib file and extract data ===

    # Upper left, Lower right
    area = [
        lat + GRIB_RESOLUTION,
        lon - GRIB_RESOLUTION,
        lat - GRIB_RESOLUTION,
        lon + GRIB_RESOLUTION,
    ]

    print("area: " + str(area))

    os.environ['CDSAPI_RC'] = cdsapircfile

    netcdf_filename = download_netcdf_from_cams(datetime.utcnow(), area, upto = tohour)
    data = extract_cams_data_java(java, jar, netcdf_filename, lat, lon)

    sort_data(data)
    if outputfile is not None:
        with open(outputfile, 'w') as f:
            print_sirane_fond_input(data, file = f)
    else:
        print_sirane_fond_input(data)
    start_time = data[0][0] # First start hour

    # cleanup
    if not keepgrib:
        os.unlink(netcdf_filename)

    return start_time


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--config")
    parser.add_argument("--tohour")
    parser.add_argument("--java")
    parser.add_argument("--jar")
    parser.add_argument("--keep-grib", action = 'store_true')
    args = parser.parse_args()

    if args.tohour is not None: args.tohour = int(args.tohour)

    main(outputfile = args.file, configfile = args.config, tohour = args.tohour, keepgrib = args.keep_grib, java = args.java, jar = args.jar)



# Old version using grib files:

# import pygrib

# # NB hope that your square doesn't happen to overlap with the 0 meridian as it will not work properly

# GRIB_RESOLUTION = 0.1
# lat1 = lat - GRIB_RESOLUTION / 2
# lat2 = lat + GRIB_RESOLUTION / 2
# lon1 = (lon - GRIB_RESOLUTION / 2 + 360) % 360
# lon2 = (lon + GRIB_RESOLUTION / 2 + 360) % 360

# data = pygrib.open(netcdf_filename)
# data = extract_cams_data(data, lat1, lat2, lon1, lon2)

# Extract MintData from the cams pygrib.open object and convert to sirane units
# def extract_cams_data (gribs, lat1, lat2, lon1, lon2):
#     r = []

#     # Loop over gribs 4 elements at a time
#     gribs = iter(gribs)
#     while True:
#         # Consider the next 4 grib entries: NO2, O3, PM10, PM2.5
#         grib_no2 = next(gribs, None)
#         if grib_no2 is None: break # No more entries
#         grib_o3, grib_pm10, grib_pm2_5 = next(gribs), next(gribs), next(gribs)

#         # Grab timestamp
#         dt = datetime(grib_no2.year, grib_no2.month, grib_no2.day, grib_no2.hour, grib_no2.minute, grib_no2.second)
#         dt += timedelta(hours = grib_no2.forecastTime)

#         # Fill data_pollu with a value from each grib
#         data_pollu = [dt]
#         for grib in [grib_no2, grib_o3, grib_pm10, grib_pm2_5]:
#             (data, lats, lons) = grib.data(lat1=lat1, lat2=lat2, lon1=lon1, lon2=lon2)
#             if data.shape == (1, 1):
#                 # We grabbed the single datapoint !
#                 p = data[0, 0]
#                 p = p * 1e9 # Convert kg/m3 to µg/m3
#                 data_pollu.append(p)
#             else:
#                 raise Exception("Multiple points in grib selection")
#         r.append(data_pollu)
    
#     return r