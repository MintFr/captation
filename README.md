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

Generates a (6-hour long) SIRANE background concentration file from Copernicus data.

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

**Requirements:** cdsapi, TODO, and a valid `.cdsapirc.climate` from [Copernicus CDS](https://cds.climate.copernicus.eu/)

```sh
CDSAPI_RC=.cdsapirc.climate ./meteo_archive.py
```

WIP it only downloads data to `download.grib` for now.

### fond_stub.py

Generates a stub SIRANE background concentration file with all concentrations set to 1. (may not work)

## Developer notes

### TODO

Use java's geotools instead of pygrib
