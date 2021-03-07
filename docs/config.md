# Configuration

## config.ini

The configuration file is an INI file as recognized by Python's configparser. A template is available at `config.ini.template`.

### Configuration variables

In the `GENERAL` section:
- `longitude` and `latitude` are the coordinates of the study area.
They are used by `meteo.py` and `fond.py` to download data for that area only.

In the `meteo` section:
- `api_key` is a valid API key from [OpenWeatherMap](https://openweathermap.org/). This is used by `meteo.py`.

In the `fond` section:
- `java11` is the path to a Java 11 command. This is needed to run `fond_extract_data`.
- `fond_jar` is the path to the `fond_extract_data-all.jar`.
- `cdsapircfile` is the path to [Copernicus ADS](https://ads.atmosphere.copernicus.eu/)' `.cdsapirc` file. It defaults to `atmosphere.cdsapirc`. See 

In the `tipitrafic` section:
- `username` and `password` provided by Info Routière. Used by `datex2.py`.

In the `emission` section:
- `nm_segment_map` is the path to the segment map file for Nantes Métropole's traffic data
- `nm_segment_map` is the path to the segment map file for Info Routière's traffic data
- `network_segment_length` is the path to the segment length file for the network

## Files

### Segment map file

A segment map file is a csv file (with header) which maps a traffic segment id to a segment id from the network file (RESEAU). There are usually multiple network ids for a single traffic id.

The first column is the network id, and the second column is the traffic data's id. Additional columns are ignored. _This order may not be intuitive, but just remember that the first column is the network id._

Here is a sample file. The 3rd column in this example is ignored.
```csv
"ID_RESEAU,N,10,0","ID_Trafic,N,255,0","Distance,N,24,15"
73,310,"35,2928380149"
1028,7075,"27,232614794"
1062,2075,"12,267833312"
```

### Segment length file

A segment length file is a csv file (with header) which maps a network (RESEAU) segment to it length in meters.

The first column is the network id, and the second column is its length in meters. Additional columns are ignored.

Here's a sample file:
```csv
ID,length
"1",1.700
"2",4.588
"3",4.305
"4",4.101
```