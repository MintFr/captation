#!/usr/bin/env python3

import os
import sys
import csv
from datetime import datetime, timezone
import functools
import configparser

from trafic_nm import main as trafic_main
from datex2 import main as datex2_main


"""
File formats:

- A segment map file is a csv file where the first column is the traffic segment id,
  and the second column is the corresponding network segment id.
  The header line is ignored, as well as additional columns (for convenience).
  cf. read_mapfile

- A network lengths file is a csv file where the first column is the network segment id,
  and the second column is the segment length in meters.
  The header line is ignored, as well as additional columns (for convenience).
  cf. read_network_lengths

Python datatypes:

- SiraneEmisLin is a dictionary of network ids mapping to 3-tuple values of form (emis_nox, emis_pm10, emis_pm2.5) in g/s
  ie. `e_NOx, e_PM10, e_PM25 = sirane_emis_lin[network_id]`
- SegmentMap is a dictionary of traffic segment ids mapping to lists of network segment ids.
  ie. `for segment_id in segment_map[traffic_id]`
- NetworkLengthMap is a dictionary of network segment ids mapping to the segment lengths in meters
  ie. `segment_length = network_length_map[network_id]`
"""


def compute_emission(speed, rate):
    """
    Compute the emissions in g/s/km given a speed in km/h and a vehicule rate in 1/h.
    They should be multiplied by the network segment's length afterwards
    """
    # TODO document data source
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
    Updates the SiraneEmisLin data in-place, based on the list of traffic_data using &find_segments and &extract_parameters

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
        emissions_per_km = compute_emission(speed, rate)

        # Update the network segments corresponding to the row data
        for segment_id, segment_length in find_segments(row):
            entry = data.get(segment_id)
            # Convert segment_length to kilometers
            emissions = [ x * segment_length / 1000 for x in emissions_per_km ]

            # Add emissions to existing ones if any
            if entry is None:
                data[segment_id] = emissions
            else:
                for i, v in enumerate(emissions):
                    entry[i] += v


def write_emislin(data, file = sys.stdout):
    """
    Write SiraneEmisLin data to file in SIRANE format.

    cf. <http://air.ec-lyon.fr/SIRANE/Article.php?&File=&Id=SIRANE_File_EmisLin&Lang=FR>
    """
    # Define our write function
    p = functools.partial(print, sep = "\t", file = file)

    # Headers
    p("Id", "NO", "NO2", "PM10", "PM25", "O3")
    
    # SIRANE wants the segment ids to be 0-based and to all be present in the emission file
    SEGMENT_COUNT = 23457 # TODO move out hardcoded value ?
    for i in range(SEGMENT_COUNT):
        k = str(i) # data keys are strings
        v = data.get(k, [0, 0, 0])
        p(i, 0, *v, 0) # NO and O3 emissions are set to 0


def write_evolemislin(data, file = sys.stdout):
    """
    Write the data of a merged EvolEmisLin and EvolEmisSurf to file, with hardcoded modulation factors.
    The modulation factor is set to 1 for linear emissions, and 0 for surface emissions.

    $data is a list of (datetime, emis_lin_filename, emis_surf_filename) tuples of type (datetime, str, str)

    NB Make sure that 'Nombre de modulations lineiques = 1' is in `Donnees.dat`
       as we only write the Mod_Lin_0_* headers

    cf. <http://air.ec-lyon.fr/SIRANE/Article.php?&File=&Id=SIRANE_File_EvolEmisLin&Lang=FR>
        and <http://air.ec-lyon.fr/SIRANE/Article.php?&File=&Id=SIRANE_File_EvolEmisSurf&Lang=FR>
    """
    # Define our write function
    p = functools.partial(print, sep = "\t", file = file)

    our_species = "NO NO2 PM10 PM25 O3".split()

    lin_headers = [ "Mod_Lin_0_%s" % x for x in our_species ]
    surf_headers = [ "Mod_Surf_%s" % x for x in our_species ]
    p("Date", "Fich_Lin", *lin_headers, "Fich_Surf", *surf_headers)

    for row in data:
        dt, filename, surf_filename = row
        p(dt.strftime("%d/%m/%Y %H:%M"),
          filename,
          *([1] * len(lin_headers)), # Linear emissions are set to 1
          surf_filename,
          *([0] * len(surf_headers))) # Surface emissions are set to 0


def read_network_lengths(segment_length_filename):
    """
    Read the network lengths file and return a NetworkLengthMap
    """

    network_lengths = {}

    with open(segment_length_filename) as f:
        reader = csv.reader(f)
        reader = iter(reader)
        _headers = next(reader) # Skip headers

        for row in reader:
            network_id = row[0]
            segment_length = float(row[1])

            network_lengths[network_id] = segment_length
    
    return network_lengths


def read_mapfile(filename):
    """
    Reads the segment map file and returns a SegmentMap.
    """
    segment_map = {}

    with open(filename) as f:
        reader = csv.reader(f)
        reader = iter(reader)
        _headers = next(reader) # Skip headers

        for row in reader:
            # We don't use `network_id, traffic_id = row` to allow ignored extra columns
            network_id = row[0]
            traffic_id = row[1]

            # Update or create the entry
            entry = segment_map.get(traffic_id)
            if entry is None:
                segment_map[traffic_id] = [network_id]
            else:
                entry.append(network_id)
    
    return segment_map


def create_find_segments(segment_map, network_lengths, get_traffic_id):
    """
    Returns a find_segments function to use in insert_emission based on
    a SegmentMap and a NetworkLengthMap and
    a function that returns the traffic segment id given a traffic data row
    """

    # Now define the working function which has the segment_map in scope
    def find_segments(traffic_row):
        segments = []

        traffic_id = get_traffic_id(traffic_row)
        for segment_id in segment_map.get(traffic_id, []):
            segment_length = network_lengths.get(segment_id)
            if segment_length is not None:
                segments.append( (segment_id, segment_length) )
        
        return segments
    
    return find_segments


# Functions to handle data from trafic_nm.py

I_NM_ID = 0
I_NM_SPEED = 6
I_NM_RATE = 4

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

I_D2_ID = 0
I_D2_SPEED = 4
I_D2_RATE = 2

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
    nm_segment_mapfile = config['emission']['nm_segment_map']
    d2_segment_mapfile = config['emission']['d2_segment_map']
    segment_length_file = config['emission']['network_segment_length']
    
    # Initialize data
    now_s = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    emis_data = {}

    # Read network lengths, needed to compute the emissions
    network_lengths = read_network_lengths(segment_length_file)

    # === trafic_nm.py ===

    # Download NM traffic data
    traffic_filename = "trafic_%s.csv" % now_s
    traffic_time = trafic_main(outputfile = traffic_filename)

    # Read mapfile
    nm_segment_map = read_mapfile(nm_segment_mapfile)
    find_nm_segments = create_find_segments(nm_segment_map, network_lengths, lambda row: row[I_NM_ID])

    # Use downloaded data to update emis_data
    with open(traffic_filename) as f:
        reader = csv.reader(f, delimiter = ";")
        reader = iter(reader)
        _headers = next(reader) # Skip headers

        insert_emission(emis_data, reader, find_nm_segments, extract_nm_parameters)
    os.unlink(traffic_filename)

    # === datex2.py ===

    # Download PC Circulation data
    datex_filename = "datex2_%s.csv" % now_s
    datex_time = datex2_main(configfile = configfile, outputfile = datex_filename)

    # Read datex2 mapfile
    d2_segment_map = read_mapfile(d2_segment_mapfile)
    find_d2_segments = create_find_segments(d2_segment_map, network_lengths, lambda row: row[I_D2_ID])

    # Use downloaded data to update emis_data
    with open(datex_filename) as f:
        reader = csv.reader(f)
        reader = iter(reader)
        _headers = next(reader) # Skip headers

        insert_emission(emis_data, reader, find_d2_segments, extract_d2_parameters)
    os.unlink(datex_filename)
    
    # Write data to output
    if outputfile is None:
        write_emislin(emis_data)
    else:
        with open(outputfile, 'w') as f:
            write_emislin(emis_data, f)
    
    return traffic_time, datex_time


if __name__ == '__main__':
    main()
