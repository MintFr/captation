#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime, timedelta, timezone

import requests


def main(outputfile = None):
    """
    Download Nantes Metropole traffic data as a csv to outputfile.

    Returns the data's creation time
    """

    if outputfile is None:
        outputfile = "trafic.%s" % fileformat

    # Create file URL
    fileformat = "csv"
    api_url = "https://data.nantesmetropole.fr/explore/dataset/244400404_fluidite-axes-routiers-nantes-metropole/download/?format=%s&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%%3B" % fileformat
    
    # Download it
    r = requests.get(api_url)
    r.raise_for_status()

    # Write it to the file
    with open(outputfile, 'wb') as f:
        f.write(r.content)

    # Reopen the file to read the data's time
    with open(outputfile) as f:
        reader = csv.reader(f, delimiter = ";")
        lines = iter(reader)
        next(lines) # skip first line (headers)
        row = next(lines)

    # Manually split the timezone offset because I'm not sure it's handled properly
    dt, offset = row[3].split("+")

    tz_val = datetime.strptime(offset, "%H:%M")
    delta = timedelta(hours = tz_val.hour, minutes = tz_val.minute)
    tz = timezone(delta)

    timestamp = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S").replace(tzinfo = tz)
    return timestamp


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help = "Output file")
    args = parser.parse_args()

    main(outputfile = args.file)
