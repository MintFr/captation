#!/usr/bin/env python3

import sys
import argparse
import csv

"""
Converts a mapfile where the column separator is a tab,
and the relevant data is in 0-indexed columns 3, 1 and 2.

ie. the header is 
```
IDOLD_RESEAU	ID_TRAFIC	DISTANCE	RESEAU_ID	RESEAU_IDOLD
```
and we're only interested in RESEAU_ID, ID_TRAFIC and DISTANCE
"""

parser = argparse.ArgumentParser()
parser.add_argument("file")

args = parser.parse_args()

with open(args.file) as f:
    reader = csv.reader(f, delimiter = "\t")
    writer = csv.writer(sys.stdout)

    reader = iter(reader)

    # Copy headers
    headers = next(reader)
    new_headers = [headers[3], headers[1], headers[2]]
    writer.writerow(new_headers)

    # Edit the first element of each row, which is the id
    for row in reader:
        id_network = row[3]
        id_traffic = row[1]
        distance = row[2]

        if id_network == "":
            continue
        writer.writerow([id_network, id_traffic, distance])