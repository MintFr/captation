#!/usr/bin/env python3
import csv
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta, date, time
from time import strptime

"""
A timings file looks like this:

    Date,Créneau,Itinéraire,Début,Fin
    18/01/21,M1,ECN,08:24:00,10:15:00
    18/01/21,M2,LAENNEC,10:28:30,11:56:10
    19/01/21,M1,ECN,08:04:10,09:24:58
    19/01/21,M2,LAENNEC,10:18:00,12:04:00
"""

parser = argparse.ArgumentParser()
parser.add_argument("--csv", required = True, help = "The CSV data file")
parser.add_argument("--times", required = True, help = "The CSV timings file")
parser.add_argument("--capteur", required = True, help = "The sensor's name which will be appended to the filename")
args = parser.parse_args()

# Slurp CSV data
with open(args.csv) as f:
    # Slurp file
    reader = csv.reader(f)
    data = list(reader)

# Slurp time entries
with open(args.times) as f:
    reader = csv.reader(f)
    timings = list(reader)

# Remove header lines
headers = data.pop(0)
timings.pop(0)

# Handle `sep=,` line in Atmo data files if it is present
if args.capteur.startswith("Atmo"):
    if headers[0].startswith("sep"):
        # Pop again as we removed the Excel metadata line before
        headers = data.pop(0)

# Convert the timestamp into a datetime object and insert it at the start
tz_fr = timezone(timedelta(hours = 1))
for row in data:
    if args.capteur.startswith("Flow"):
        row.insert(0, datetime.fromtimestamp(int(row[0]), tz = tz_fr))
    elif args.capteur.startswith("Atmo"):
        row.insert(0, datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S").replace(tzinfo = tz_fr))
    else:
        raise Exception("Unknown CSV data format: could not find timestamp")

# Convert timings entries to date and time objects
for row in timings:
    mydate = date(*(strptime(row[0], "%d/%m/%y")[:3]))
    starttime = time(*(strptime(row[3], "%H:%M:%S")[3:6]))
    endtime = time(*(strptime(row[4], "%H:%M:%S")[3:6]))
    row[0] = mydate
    row[3] = datetime.combine(mydate, starttime, tz_fr)
    row[4] = datetime.combine(mydate, endtime, tz_fr)

# Create output directory and enter into it
try:
    os.mkdir("split_data")
except FileExistsError:
    pass
os.chdir("split_data")

# Use timings to select the subset of data within that time interval (and write it a file)
for timing in timings:
    print(timing[0].isoformat(), *timing[1:3], timing[3].isoformat(),timing[4].isoformat())
    subset = list(filter(lambda x: timing[3] <= x[0] <= timing[4], data))

    # [0]: first line, [0][0]: timestamp of the first line
    try:
        date_s = subset[0][0].strftime("%Y-%m-%d")
    except IndexError:
        print("No data found between %s and %s" % (timing[3].isoformat(), timing[4].isoformat()))
        continue # skip current iteration

    direction = timing[2]
    creneau = timing[1]
    capteur = args.capteur

    outfilename = "%s_%s_%s_%s.csv" % (date_s, direction, creneau, capteur)
    with open(outfilename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in subset:
            writer.writerow(row[1:])
        print("-> split_data/%s" % outfilename)
