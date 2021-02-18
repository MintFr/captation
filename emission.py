#!/usr/bin/env python3

import os
import csv
from datetime import datetime

from trafic_nm import main as trafic_main
from datex2 import main as datex2_main


# TODO do we actually want compute_emission to return emissions grams for a period of 15minutes ?
#      Wouldn't it be more useful to have it return the g/km emission for a period of an our ?
#      This depends on how the emissions are entered into the model

V    = [       10,       30,       60,       90,       11,      130 ] # km/h
NOx  = [     0.55,     0.38,     0.28,     0.30,     0.42,     0.58 ] # g/km
PM10 = [ 0.005886, 0.004578, 0.001730, 0.004578, 0.006540, 0.007848 ] # g/km
PM25 = [ 0.003114, 0.002422,  0.00173, 0.002422,  0.00346, 0.004152 ] # g/km

def compute_emission(speed, rate, distance):
    """
    Compute the emissions in grams for a period of 15 minutes
    given a speed in km/h, a vehicule rate in 1/h and a distance in km
    """
    # Find interval
    i_last = len(V) - 1
    if speed < V[0]:
        i_left, i_right = 0, 0
    elif speed > V[i_last]:
        i_left, i_right = i_last, i_last
    else:
        i = 1
        while not speed <= V[i]:
            i += 1
        i_left, i_right = i-1, i

    # Define interpolation
    if i_left != i_right:
        t = (speed - V[i_left]) / (V[i_right] - V[i_left])
    else:
        t = 1 # When speed is ≤ 10 or > 130
    def interpolate(points):
        return t * points[i_left] + (1-t) * points[i_right]
    
    # We use divide by 4 because we compute per ¼ hour
    e_NOx = interpolate(NOx) * rate * distance / 4
    e_PM10 = interpolate(PM10) * rate * distance / 4
    e_PM25 = interpolate(PM25) * rate * distance / 4

    return e_NOx, e_PM10, e_PM25


now_s = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
configfile = "config.ini"


# === Compute emissions based on the NM traffic data ===

# Download the traffic data
traffic_filename = "trafic_%s.csv" % now_s
traffic_time = trafic_main(outputfile = traffic_filename)

with open(traffic_filename) as f:
    reader = csv.reader(f, delimiter = ";")
    
    # NB missing values are represented by -1
    i_distance = 2
    i_rate = 4
    i_speed = 6

    reader = iter(reader)
    _headers = next(reader) # Skip headers
    for row in reader:
        speed = int(row[i_speed])
        rate = int(row[i_rate])
        distance = int(row[i_distance]) / 1000 # Convert m to km

        if rate == -1 or speed == -1:
            if rate == 0:
                e_NOx, e_PM10, e_PM25 = 0, 0, 0
            else:
                # NB We skip values where data is unavailable
                continue

        e_NOx, e_PM10, e_PM25 = compute_emission(speed, rate, distance)
        print(e_NOx, e_PM10, e_PM25) #  TODO do something useful here

# Delete downloaded traffic file
os.unlink(traffic_filename)


# === Compute emissions based on PC Circulation data ===

# Download the traffic data
datex_filename = "datex2_%s.csv" % now_s
datex_time = datex2_main(configfile = configfile, outputfile = datex_filename)

with open(datex_filename) as f:
    reader = csv.reader(f)
    
    # Missing values are represented as empty strings
    i_rate = 2
    i_speed = 4

    reader = iter(reader)
    _headers = next(reader) # Skip headers
    for row in reader:

        try:
            speed = int(row[i_speed])
        except:
            continue # Skip missing values
        rate = int(row[i_rate])
        distance = 1 # in km*km^-1 (unitless, so that the emissions are in g/km for 15min)

        # TODO handle missing values

        e_NOx, e_PM10, e_PM25 = compute_emission(speed, rate, distance)
        print(e_NOx, e_PM10, e_PM25) #  TODO do something useful here

# TODO if we really want the emissions to be multiplied by the road's length
# We should probably cross reference the ID with a hash of road_id to road_length
