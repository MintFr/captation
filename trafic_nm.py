#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime, timedelta, timezone

import requests

# TODO Choisir le format le plus approprié ici: <https://data.nantesmetropole.fr/explore/dataset/244400404_fluidite-axes-routiers-nantes-metropole/export/>
#      Formats disponibles: CSV, JSON, Excel, GeoJSON, Shapefile, KML


def main(outputfile = None):
    """
    Returns the data's creation time
    """
    # On télécharge pour l'instant les données au format CSV
    fileformat = "csv"
    api_url = "https://data.nantesmetropole.fr/explore/dataset/244400404_fluidite-axes-routiers-nantes-metropole/download/?format=%s&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%%3B" % fileformat

    if outputfile is None:
        outputfile = "trafic.%s" % fileformat
    
    r = requests.get(api_url)
    r.raise_for_status()

    with open(outputfile, 'wb') as f:
        f.write(r.content)

    # Reopen the file to read the data's time
    with open(outputfile) as f:
        reader = csv.reader(f, delimiter = ";")
        lines = iter(reader)
        next(lines) # skip first line (headers)
        row = next(lines)

    # manually split the timezone offset because I'm not sure it's handled properly
    dt, offset = row[3].split("+")

    tz_val = datetime.strptime(offset, "%H:%M")
    delta = timedelta(hours = tz_val.hour, minutes = tz_val.minute)
    tz = timezone(delta)

    dt = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S").replace(tzinfo = tz)
    return dt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help = "Output file")
    args = parser.parse_args()

    main(outputfile = args.file)
