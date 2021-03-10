# captation

Scripts for the measurement team.

`model/` contains scripts to run the model, `scripts/` contains helper scripts or unfinished scripts. `sirane/` is an empty folder in which you should put the (Linux) SIRANE executable, and it's input folder `INPUT`.

## Installation

%% TODO build tarball %%

Set up the Python environment and install dependencies:

```sh
# Create a virtual environment in venv, and activate it
python3 -m venv venv
. venv/bin/activate

# Install dependencies
./install_requirements.py

# Close the virtual environment
deactivate
```

Create the configuration file `config.ini` using `config.ini.template` as a template. See also the documentation at `docs/config.md`.

## Usage

Launch the model:

```sh
# Activates the virtual env and launches the model
./model.sh
```

If you don't have enough RAM (like me), you could try leveraging a virtual machine and swap space, or use Linux cgroups and swap like so:

```sh
# (as root) Create a 10G swapfile
fallocate -l 10G swapfile
mkswap swapfile
swapon swapfile

# Run it with a RAM limit of 1G (but unlimited swap)
systemd-run --scope -p MemoryMax=1G ./model.sh
```

Just know that swap is very slow compared to RAM (30 minutes vs 8 hours).

## Documentation

See the `README.md` files in each of the folders.

## Developer notes

The server we're trying to deploy these scripts on is a Debian Stretch install.

One of the requirements was that the scripts are simple to deploy on a server. Since pygrib was hard to install, we had to use Java instead (see `fond_extract_data`).

Make sure to handle timezones correctly: everything is in UTC, even SIRANE input… except when it's not (sensor data files are generally in GMT+1 or a slowly drifting clock for the Fidas).

The fact that we're working with the species `NO2 O3 PM10 PM25` is generally hardcoded in the scripts. Same issue with the number of segments in the network file.

The model doesn't _seem to_ to run properly if there are no surface emission grids defined. So we create one, and set the modulation factor to 0.

### TODO

- For some reason SIRANE outputs a netcdf file that is not recognized as a raster by QGIS (it uses `x, y` instead of `lat, lon`). It works properly with `raster2pgsql` though.

- `raster2pgsql` and PostGIS's `ST_Translate` (see MintServ) seem to not work on the server (Debian Stretch), something about the gdal library. If it's only `raster2pgsql` which doesn't work, a solution would be to make SIRANE output in ASCII format, which we will then parse and convert to a format which works with the server's `raster2pgsql`. Maybe using the format Arc/Info ASCII Grid which is easy to write, although it requires square cells.

  A manual one-off workaround is to convert the netcdf to the osm projection with QGIS, and then import that using raster2pgsql on your machine. This skips using `ST_Translate`

- Write a script that cleans up the output directory as well as the temporary download directory. This is especially important since MintServ (the database importer) will import the first file present in the output directory. (Also add an option to not delete them but to rename them to something else)

### Documentation status

```text
--    model/
OK      README.md
        model.py
OK      datex2.py
OK      emission.py
OK      meteo.py
OK      trafic_nm.py
--    fond_extract_data/
OK      README.md
OK      src/main/java/fr/nantral/mint/capta/FondApp.java
--    scripts/
OK      convert_mapfile_from_1based_to_0based.py
OK      convert_mapfile_from_mixed_to_normal.py
OK      cut_data.py
OK      meteo_archive.py
MEH     meteo_ncep.py
OK      random_emis_lin.pl
OK      simuvia.py
```
