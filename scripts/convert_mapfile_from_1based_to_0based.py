#!/usr/bin/env python3

import sys
import argparse
import csv

"""
Converts a 1-based network id to a 0-based network id in a mapfile
"""

parser = argparse.ArgumentParser()
parser.add_argument("file")

args = parser.parse_args()

with open(args.file) as f:
    reader = csv.reader(f)
    writer = csv.writer(sys.stdout)

    reader = iter(reader)

    # Copy headers
    headers = next(reader)
    writer.writerow(headers)

    # Edit the first element of each row, which is the id
    for row in reader:
        id = int(row[0])
        new_id = id - 1
        writer.writerow([new_id, *row[1:]])
