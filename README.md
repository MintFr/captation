# captation

Scripts for the measurement team.

`model/` contains scripts to run the model, `scripts/` contains helper scripts or unfinished scripts.

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

## Documentation

See the `README.md` files in each of the folders.

## Developer notes

%% TODO explain pygrib and fond_extract_data %%

pygrib was hard to install on the server, which is why we use java instead

The fact that we're working with `NO2 O3 PM10 PM25` is generally hardcoded in the scripts

The model doesn't want to run if there are no surface emission grids defined ??

### TODO

Handle timezones correctly: meteo.py and fond.py are in UTC, SIRANE expects GMT+1 (probably) (Actually, it expects UTC)

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