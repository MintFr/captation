#!/usr/bin/env python3
import csv
import os
import argparse
from datetime import datetime, timezone, timedelta, date, time
from time import strptime

parser = argparse.ArgumentParser()
parser.add_argument("--csv", required = True)
parser.add_argument("--times", required = True)
parser.add_argument("--capteur", required = True)
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

# Convert the timestamp into a datetime object
tz_fr = timezone(timedelta(hours = 1))
for row in data:
    row.insert(0, datetime.fromtimestamp(int(row[0]), tz = tz_fr))

for row in timings:
    print(row)
    mydate = date(*(strptime(row[0], "%d/%m/%y")[:3]))
    starttime = time(*(strptime(row[3], "%H:%M:%S")[3:6]))
    endtime = time(*(strptime(row[4], "%H:%M:%S")[3:6]))
    row[0] = mydate
    row[3] = datetime.combine(mydate, starttime, tz_fr)
    row[4] = datetime.combine(mydate, endtime, tz_fr)

# Create output directory and change to it
try:
    os.mkdir("split_data")
except FileExistsError:
    pass
os.chdir("split_data")


for timing in timings:
    print(timing[0].isoformat(), *timing[1:3], timing[3].isoformat(),timing[4].isoformat())
    subset = list(filter(lambda x: timing[3] <= x[0] <= timing[4], data))

    date_s = subset[0][0].strftime("%Y-%m-%d")

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
