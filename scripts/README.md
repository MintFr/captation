# Scripts

One-off scripts, or helper scripts for other measurement team activities.

## convert_mapfile_from_1based_to_0based.py

Convert the ids in a mapfile (see `config.md`) to be 1-indexed, to be 0-indexed.

For some reason, if the ids in the emission files start at 1 instead of 0, SIRANE complains.

Usage:
```sh
./convert_mapfile_from_1based_0based.py 1based_mapfile.csv > 0based_mapfile.csv
```

## convert_mapfile_from_mixed_to_normal.py

Convert the mapfile csv provided by A.L. where the columns are not in the right order, into a mapfile as expected by `emission.py`.

It also removes entries where values are missing.

Usage:
```sh
./convert_mapfile_from_mixed_to_normal.py al_mapfile.csv > normal_mapfile.csv
```

## cut_data.py

Cuts a Flow or Atmo measurements CSV file into smaller files based on a timing CSV file. It writes the created files into `split_data`.

The script detects which column contains the timestamp based on the
`--capteur` argument passed on the command line.

Usage:
```sh
# Creates a bunch of files in split_data/ named *_Flow3.csv.
# It leaves a 1 minute padding before and after the times specified in the timing file
./cut_data.py --csv data/Flow3_user_measures_20210118_20210201.csv --times data/Horaires_Flow3.csv --capteur Flow3 --minutes-margin 1
```

The timings file looks like the following. Times are in GMT+1 and dates in DD/MM/YY format.

```csv
Date,Créneau,Itinéraire,Début,Fin
18/01/21,M1,ECN,08:24:00,10:15:00
18/01/21,M2,LAENNEC,10:28:30,11:56:10
19/01/21,M1,ECN,08:04:10,09:24:58
19/01/21,M2,LAENNEC,10:18:00,12:04:00
```

The Atmotrack files have a 2 line header: the weird Excel metadata line `sep=,` and the actual CSV header.\
We combined all the files into a single (normal) csv using this command:
```sh
perl -nle 'if ($. == 2) { print && exit }' 210120_atmotrack_data.csv > Atmo3_atmotrack_data.csv
tail -qn +3 2101*.csv >> Atmo3_atmotrack_data.csv # Beware of infinite loops
```

## meteo_archive.py

**WIP:** It currently only downloads the grib file using cdsapi.

**Requirements:** cdsapi and a valid `climate.cdsapirc` from [Copernicus CDS](https://cds.climate.copernicus.eu/)

Usage:
```sh
CDSAPI_RC=climate.cdsapirc ./meteo_archive.py
```

## meteo_ncep.py

**NB:** This script requires `pygrib` which couln't be installed on the server, so it hasn't been tested thoroughtly.
It is only kept for future reference.

**Requirements:** pygrib

Reads a GRIB file downloaded from [NCEP](https://www.nco.ncep.noaa.gov/pmb/products/gfs/), and prints the SIRANE weather file to the terminal.

The datapoint is hardcoded to be Nantes.

Usage:
```sh
# Print weather data from NCEP grib in SIRANE format
./meteo_ncep.py weather_file.grib
```

## random_emis_lin.pl

Perl (!) script that writes a random emission file with `$count` lines.

It writes entries for network identifiers 0 to `$count-1`.

Usage:
```sh
# Write a random emission file for a network with 23457 segments
./random_emis_lin.pl 23457 > emis_lin.dat
```

## simuvia.py

**NB:** This was a one off script. We couln't run Copert on the server, so it was only for testing purposes.

Print some weather data downloaded from OpenWeatherMap as a csv file for Copert.

It grabs weather data for Nantes.

Usage:
```sh
./simuvia.py OPENWEATHERMAP_API_KEY
```
