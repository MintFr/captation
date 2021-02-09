#!/usr/bin/env python3
import argparse
import os
import sys
import shutil
import subprocess
from datetime import datetime, timezone, timedelta

from meteo import main as meteo_main
from fond import main as fond_main

# WARN SIRANE's directory is hardcoded as being "sirane"


def edit_donnees_dat(start_time_s, end_time_s, donnees_dat_path, output_filename):
    """
    Edit the Donnees.dat at $donnees_dat_path and write the output to $output_filename.
    We edit in the simulation start and end times based on the strings $start_time_s and $end_time_s
    """
    # Slurp lines
    with open(donnees_dat_path) as f:
        donnees_lines = list(f)

    # Write to the output file
    with open(output_filename, 'w') as f:
        for line in donnees_lines:
            # Insert simulation start and end times
            if line.startswith("Date de debut"):
                line = "Date de debut = %s\n" % start_time_s
            if line.startswith("Date de fin"):
                line = "Date de fin = %s\n" % end_time_s
            
            f.write(line)

def launch_model():
    """
    Launch the model in its directory using the "default" input files configuration layout.
    """
    # Flush stdout and stderr before launching the model so that it displays
    # buffered output before the subprocess's output
    sys.stdout.flush()
    sys.stderr.flush()

    # Run SIRANE in sirane/ directory
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
        sys.stdout.flush()
        meteo_start = meteo_main(outputfile = meteo_output, configfile = configfile)

        # Create fond file
        fond_output = "sirane/fond_%s.dat" % timestamp
        print("Creating fond file at %s" % fond_output)
        sys.stdout.flush()
        fond_start = fond_main(outputfile = fond_output, configfile = configfile)
    else:
        print("Skipped fetching data from network sources")

    # Compute simulation start and end times
    start_time = max(meteo_start, fond_start)
    end_time = start_time + timedelta(hours = 3) # FIXME hardcoded 3 hour simulation
    start_time_s = start_time.strftime("%d/%m/%Y %H:%M:%S")
    end_time_s = end_time.strftime("%d/%m/%Y %H:%M:%S")

    # Edit INPUT/Donnees.dat
    print("Editing Donnees.dat")
    edit_donnees_dat(start_time_s, end_time_s, "sirane/INPUT/Donnees.dat", "sirane/new_donnees.dat")
    shutil.move("sirane/new_donnees.dat", "sirane/INPUT/Donnees.dat")
    
    # Copy data files
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
