#!/usr/bin/env python3

import os
import sys
import csv
from datetime import datetime
import functools
import configparser

from trafic_nm import main as trafic_main
from datex2 import main as datex2_main


"""
Types:
- SiraneEmisLin is a dictionary of integer keys mapping to 3-tuple values of form (emis_no2, emis_pm10, emis_pm2.5) in g/s
"""


def compute_emission(speed, rate):
    """
    Compute the emissions in g/s/km given a speed in km/h and a vehicule rate in 1/h.
    They should be multiplied by the network segment's length afterwards
    """
    V    = [       10,       30,       60,       90,       11,      130 ] # km/h
    NOx  = [     0.55,     0.38,     0.28,     0.30,     0.42,     0.58 ] # g/km
    PM10 = [ 0.005886, 0.004578, 0.001730, 0.004578, 0.006540, 0.007848 ] # g/km
    PM25 = [ 0.003114, 0.002422,  0.00173, 0.002422,  0.00346, 0.004152 ] # g/km

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
    
    # We divide by 3600 to convert to /s from g/h
    e_NOx = interpolate(NOx) * rate / 3600
    e_PM10 = interpolate(PM10) * rate / 3600
    e_PM25 = interpolate(PM25) * rate / 3600

    return e_NOx, e_PM10, e_PM25


class SkipEmissionComputation(Exception):
    """See &extract_parameters in insert_emission()"""
    pass

def insert_emission(data, traffic_data, find_segments, extract_parameters):
    """
    Updates $data in-place, based on $trafic_data using &find_segments and &extract_parameters

    $data is of type SiraneEmisLin
    $traffic_data is an iterable of rows
    &find_segments(row) is a function that takes a row (from $traffic_data) and returns a list of tuples
                        of (segment_id, segment_length), with the length in meters
    &extract_parameters(row) is a function that takes a row (from $traffic_data) and
                        returns a tuple of (speed, rate) in the right units for compute_emission.
                        It may throw a SkipEmissionComputation exception to skip the current datapoint
    """

    for row in traffic_data:
        try:
            speed, rate = extract_parameters(row)
        except SkipEmissionComputation:
            continue
        distance_emissions = compute_emission(speed, rate)

        # Find network segments corresponding to the row data
        for segment_id, segment_length in find_segments(row):
            # Convert segment_length to kilometers
            emissions = [ x * segment_length / 1000 for x in distance_emissions ]
            data[segment_id] = emissions


def write_emislin(data, file = sys.stdout):
    """
    $data is of type SiraneEmisLin
    cf. <http://air.ec-lyon.fr/SIRANE/Article.php?&File=&Id=SIRANE_File_EmisLin&Lang=FR>
    """
    # Define our write function
    p = functools.partial(print, sep = "\t", file = file)

    p("Id", "NO2", "PM10", "PM25")

    for k in sorted(data.keys()):
        v = data[k]
        p(k, *v)


def write_evolemislin(data, file = sys.stdout):
    """
    NB the values are unmodulated by SIRANE, so the values are set to 1
    NB The file is also used for surface emissions, so we also need those headers
       Since we don't use surface emissions, the modulation factor is set to 0

    NB make sure that 'Nombre de modulations lineiques = 1' is in Donnees.dat

    $data is a list of (datetime, filename) tuples of type (datetime, str)
    """
    # Define our write function
    p = functools.partial(print, sep = "\t", file = file)

    our_species = "NO NO2 PM10 PM25 O3".split()
    surf_headers = [ "Mod_Surf_%s" % x for x in our_species ]
    lin_headers = [ "Mod_Lin_0_%s" % x for x in our_species ]
    p("Date", "Fich_Lin", *lin_headers, "Fich_Surf", *surf_headers)
    for row in data:
        dt, filename, surf_filename = row
        p(dt.strftime("%d/%m/%Y %H:%M"),
          filename,
          *([1] * len(lin_headers)),
          surf_filename,
          *([0] * len(surf_headers)))


# Functions to handle data from trafic_nm.py

I_NM_SPEED = 6
I_NM_RATE = 4
I_NM_ID = 0

def create_find_nm_segments(map_filename):
    """
    Reads the contents of $map_filename and returns the a find_segments function
    to use in insert_emission

    map_filename is the filename as described by config.ini's nm_segment_map
    """
    nm_segment_map = {}

    # Read map file, and fill in nm_segment_map
    with open(map_filename) as f:
        reader = csv.reader(f)
        reader = iter(reader)
        _headers = next(reader) # Skip headers

        for row in reader:
            network_id = row[0]
            traffic_id = row[1]

            entry = nm_segment_map.get(traffic_id)
            if entry is None:
                # We don't have a reference to it, so insert it
                nm_segment_map[traffic_id] = [network_id]
            else:
                # Update the list
                entry.append(network_id)

    # Now define the working function which has nm_segment_map in scope
    def find_nm_segments(traffic_row):
        """
        $nm_segment_map is a map of NM traffic IDs to lists of network (RESEAU) ids
        """
        segments = nm_segment_map.get(traffic_row[I_NM_ID])
        if segments is None:
            segments = []

        # TODO add segment length in segments [str] -> [(str, int)]

        return segments
    
    return find_nm_segments

def extract_nm_parameters(traffic_row):
    speed = int(traffic_row[I_NM_SPEED])
    rate = int(traffic_row[I_NM_RATE])

    # Handle cases where speed OR rate are -1 (ie. missing value)
    if rate == -1 or speed == -1:
        if rate == 0:
            speed = 0
        else:
            # Can't fix it, just ignore this datapoint
            raise SkipEmissionComputation()

    return speed, rate


# Functions to handle data from datex2.py

I_D2_SPEED = 4
I_D2_RATE = 2

def find_d2_segments(traffic_row):
    segments = []

    # TODO find segments

    return segments

def extract_d2_parameters(traffic_row):
    # NB Missing values are empty strings
    try:
        speed = int(traffic_row[I_D2_SPEED])
    except ValueError:
        # Missing speed, ignore this datapoint
        raise SkipEmissionComputation()

    rate = int(traffic_row[I_D2_RATE])

    return speed, rate


def main(configfile = None, outputfile = None):
    if configfile is None:
        configfile = "config.ini"

    # Read configuration file
    config = configparser.ConfigParser()
    config.read(configfile)
    nm_segment_map = config['emission']['nm_segment_map']
    
    # Initialize data
    now_s = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    emis_data = {}

    # Download and use NM traffic data
    traffic_filename = "trafic_%s.csv" % now_s
    traffic_time = trafic_main(outputfile = traffic_filename)
    find_nm_segments = create_find_nm_segments(nm_segment_map)
    with open(traffic_filename) as f:
        reader = csv.reader(f, delimiter = ";")
        reader = iter(reader)
        _headers = next(reader) # Skip headers

        insert_emission(emis_data, reader, find_nm_segments, extract_nm_parameters)
    os.unlink(traffic_filename)

    # Download and use PC Circulation traffic data
    datex_filename = "datex2_%s.csv" % now_s
    datex_time = datex2_main(configfile = configfile, outputfile = datex_filename)

    with open(datex_filename) as f:
        reader = csv.reader(f)
        reader = iter(reader)
        _headers = next(reader) # Skip headers

        insert_emission(emis_data, reader, lambda row: [], extract_d2_parameters) # FIXME lambda row: []
    os.unlink(datex_filename)
    
    if outputfile is None:
        write_emislin(emis_data)
    else:
        with open(outputfile, 'w') as f:
            write_emislin(emis_data, f)
    
    return traffic_time, datex_time


if __name__ == '__main__':
    main()