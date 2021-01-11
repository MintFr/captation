# captation

Scripts for the measurement team.

## Usage

* Copy the `config.ini.template` file to `config.ini` and fill in the required information.
* Install the dependencies as listed below
* Run the script

## Scripts

### meteo.py

**Requirements:** requests, and a valid API key from [OpenWeatherMap](https://openweathermap.org/)

```sh
./meteo.py
# or
./meteo.py --file meteo.dat
```

### fond.py

**Requirements:** cdsapi, pygrib, and a valid `~/.cdsapi` from [Copernicus ADS](https://ads.atmosphere.copernicus.eu/)
