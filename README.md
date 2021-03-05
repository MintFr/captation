# captation

Scripts for the measurement team.

`model/` contains scripts to run the model, `scripts/` contains helper scripts or unfinished scripts.

## Installation

%% TODO build tarball %%

Set up the environment and install dependencies:

```sh
# Create a virtual environment in venv, and activate it
python3 -m venv venv
. venv/bin/activate

# Install dependencies
./install_requirements.py

# Close the virtual environment
deactivate
```

Create the configuration file `config.ini` using `config.ini.template` as a template.

## Usage

Launch the model:

```sh
# Activates the virtual env and launches the model
./model.sh
```

## Configuration file

`nm_segment_map` is the name of the csv file (with header) which maps a NM traffic id to ids in the network file (RESEAU).

Here is a sample file. The 3rd column is superfluous
```csv
"ID_RESEAU,N,10,0","ID_Trafic,N,255,0","Distance,N,24,15"
73,310,"35,2928380149"
1028,7075,"27,232614794"
1062,2075,"12,267833312"
```

`network_segment_length` is the name of the csv file (with header) which maps a network (RESEAU) segment to it length in meters.

Here's a sample file.
```csv
ID,length
"1",1.700
"2",4.588
"3",4.305
"4",4.101
```

## Scripts

#### fond_extract_grib



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

Depends on requests.

Download a trafic data file from [Opendata Nantes Metropole](https://data.nantesmetropole.fr/explore/dataset/244400404_fluidite-axes-routiers-nantes-metropole/export/)
```sh
./trafic_nm.py --file trafic_file.csv
```

Sample downloaded file:
```csv
Identifiant;Nom du tronçon;Longueur;Horodatage;Débit;Taux d'occupation;Vitesse;Temps de parcours;Code couleur;etat_trafic;Geométrie;geo_point_2d
772;Vannes I9;410;2021-03-01T10:44:00+01:00;360;8.3;16;93;3;Fluide;"{""type"": ""LineString"", ""coordinates"": [[-1.582270101540026, 47.2352686493068], [-1.577780721076294, 47.23319125926304]]}";47.2342299543,-1.58002541131
9;Schuman I5;309;2021-03-01T10:44:00+01:00;480;5.8;21;54;3;Fluide;"[OMITTED]";47.2345655211,-1.56626783147
5043;Anglais I5;207;2021-03-01T10:44:00+01:00;480;6.6;18;42;3;Fluide;"[OMITTED]";47.2286549348,-1.57591504116
```

### datex2.py

Depends on requests.

Get data from [Info-Routière](http://diffusion-numerique.info-routiere.gouv.fr/toutes-les-dir-a10.html) and convert it to a CSV file.
It specifically fetches the latest traffic data (DataTR) for Nantes.

```sh
./datex2.py
# Write to output.csv with a custom config
./datex2.py --file output.csv --config local/config.ini
# *also* print DataTRT in csv format to output
./datex2.py --trt
```

Sample file:
```csv
measurementSiteReference,measurementTimeDefault,TrafficFlow,TrafficConcentration,TrafficSpeed,numberOfInputValuesUsed
MWL44.S2,2021-03-02T15:11:00+01:00,0,0,0,0
MWL44.S1,2021-03-02T15:11:00+01:00,33,6,88,33
MWn44.G1,2021-03-02T15:11:00+01:00,41,7,67,41
```

### fond_stub.py

Generates a stub SIRANE background concentration file with all concentrations set to 1. (may not work)

## Developer notes

pygrib was hard to install on the server, which is why we use java instead

The fact that we're working with `NO2 O3 PM10 PM25` is generally hardcoded in the scripts

The model doesn't want to run if there are no surface emission grids defined ??

### TODO

Handle timezones correctly: meteo.py and fond.py are in UTC, SIRANE expects GMT+1 (probably)
