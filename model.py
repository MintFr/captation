#!/usr/bin/env python3
import argparse
import os
import sys
import shutil
import subprocess
from datetime import datetime, timezone, timedelta

from meteo import main as meteo_main
from fond import main as fond_main

def launch_model():
    # Flush stdout and stderr, because they're buffered
    sys.stdout.flush()
    sys.stderr.flush()

    # Run SIRANE in sirane/ directory
    # WARN hardcoded command
    cmd = ["./sirane-rev128-etudiants-Linux64", "INPUT/Donnees.dat", "Log.txt"]
    subprocess.run(cmd, cwd = "sirane")


def main(configfile = None, skip_download = None):
    if configfile is None:
        configfile = "config.ini"
    skip_download = bool(skip_download)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

    # TODO download more data
    if not skip_download:
        print("Fetching data…")

        # Create meteo file
        meteo_output = "sirane/meteo_%s.dat" % timestamp
        print("Creating meteo file at %s" % meteo_output)
        meteo_start = meteo_main(outputfile = meteo_output, configfile = configfile)

        # Create fond file
        fond_output = "sirane/fond_%s.dat" % timestamp
        print("Creating fond file at %s" % fond_output)
        fond_start = fond_main(outputfile = fond_output, configfile = configfile)
    else:
        print("Skipped fetching data from network sources")

    start_time = max(meteo_start, fond_start)

    # Edit INPUT/Donnee.dat
    with open("sirane/INPUT/Donnees.dat") as f:
        donnees_lines = list(f)
    with open("sirane/new_donnees.dat", 'w') as f:
        for line in donnees_lines:
            # TODO add start and end times
            if line.startswith("Date de debut"):
                start_time_s = start_time.strftime("%d/%m/%Y %H:%M:%S")
                line = "Date de debut = %s\n" % start_time_s
                print("Start time is %s" % start_time_s)
            if line.startswith("Date de fin"):
                # FIXME hardcoded 3 hour simulation
                end_time_s = (start_time + timedelta(hours = 3)).strftime("%d/%m/%Y %H:%M:%S")
                line = "Date de fin = %s\n" % end_time_s
                print("End time is %s" % end_time_s)
            f.write(line)
    shutil.move("sirane/new_donnees.dat", "sirane/INPUT/Donnees.dat")

    print("Copying files")
    shutil.move(meteo_output, "sirane/INPUT/METEO/Meteo.dat")
    shutil.move(fond_output, "sirane/INPUT/FOND/Concentration_Fond.dat")

    # Launch model
    print("Launch model")
    launch_model()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--skip-download", action = "store_true")
    args = parser.parse_args()

    main(configfile = args.config, skip_download = args.skip_download)
