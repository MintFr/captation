# captation

Scripts for the measurement team.

## Usage

* Copy the `config.ini.template` file to `config.ini` and fill in the required information.
* Install the dependencies as listed below
* Run the script

## Scripts

### meteo.py

**WARN:** The date values are in UTC and not GMT+1.

Generates a SIRANE weather input file from OpenWeatherMap data.

**Requirements:** requests, and a valid API key from [OpenWeatherMap](https://openweathermap.org/)

```sh
# Print data to STDOUT
./meteo.py
# Write data to meteo.dat
./meteo.py --file meteo.dat
# Use custom config file
./meto.py --config local/config.ini
```

### fond.py

**WARN:** Times are in UTC and not GMT+1

Generates a (24-hour long) SIRANE background concentration file from Copernicus data.

**Requirements:** cdsapi, pygrib, and a valid `atmosphere.cdsapi` from [Copernicus ADS](https://ads.atmosphere.copernicus.eu/)

```sh
# Download and print background pollution
./fond.py
# Download to fond.dat based on custom config file
./fond.py --file fond.dat --config local/config.ini
# Download forecasts up to 24:00 (instead of 06:00)
./fond.py --tohour 24
```

### meteo_archive.py

**WIP:** Only cdsapi download

**Requirements:** cdsapi, TODO, and a valid `.cdsapirc.climate` from [Copernicus CDS](https://cds.climate.copernicus.eu/)

```sh
CDSAPI_RC=.cdsapirc.climate ./meteo_archive.py
```

WIP it only downloads data to `download.grib` for now.

### cut_data.py

Cuts a Flow measurements CSV file into smaller files based on a timing CSV file.

```sh
# Creates a bunch of files in split_data/
./cut_data.py --csv data/Flow3_user_measures_20210118_20210201.csv --times data/Horaires_Flow3.csv --capteur Flow3
```

The timings file looks like the following. Times are in GMT+1 and dates in DD/MM/YY format.

```csv
Date,Créneau,Itinéraire,Début,Fin
18/01/21,M1,ECN,08:24:00,10:15:00
18/01/21,M2,LAENNEC,10:28:30,11:56:10
19/01/21,M1,ECN,08:04:10,09:24:58
19/01/21,M2,LAENNEC,10:18:00,12:04:00
```

The Atmotrack files have a 2 line header: the the Excel metadata line `sep=,` and the actual CSV header.
We combined all the files together using this command:
```sh
perl -nle 'if ($. == 2) { print && exit }' 210120_atmotrack_data.csv > Atmo3_atmotrack_data.csv
tail -qn +3 2101*.csv >> Atmo3_atmotrack_data.csv # Beware of infinite loops
```

### trafic_nm.py

Download a trafic data file from [Opendata Nantes Metropole](https://data.nantesmetropole.fr/explore/dataset/244400404_fluidite-axes-routiers-nantes-metropole/export/)
```sh
./trafic_nm.py --file trafic_file_.csv
```

### datex2.py

**WIP:** conversion is working, missing download

Get data from [Info-Routière](http://diffusion-numerique.info-routiere.gouv.fr/toutes-les-dir-a10.html) and convert it to a CSV file.

```sh
./datex2.py
```


### fond_stub.py

Generates a stub SIRANE background concentration file with all concentrations set to 1. (may not work)

## Developer notes

### TODO

Use java's geotools instead of pygrib

Handle timezones correctly: meteo.py and fond.py are in UTC, SIRANE expects GMT+1 (probably)
