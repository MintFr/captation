# fond_extract_data

A Java app that extracts the data wanted by fond.py from a netcdf file.

## Building and running

```sh
# For IntelliJ
./gradlew run --args="-netcdf data/fond_2021-02-12.nc -lat 47.2172500 -lon -1.5533600"
# For terminal
./gradlew shadowJar
java -jar build/libs/fond_extract_data-all.jar -netcdf data/fond_2021-02-12.nc -lat 47.2172500 -lon -1.5533600
```

## Description

`fond.py` downloads a netcdf file containing the background pollution concentrations for different chemicals for every hour in a specific area.\
`fond_extract_data` takes that file, and spits out a single data point for each hour and chemical species.

The species that we are interested in are NO2, O3, PM10 and PM2.5.

The output format looks like the following. It is meant to be easy to parse in Python.

```text
FORECAST time from 20210212
time: 0.0 1.0 2.0 3.0 4.0 5.0
no2_conc: 5.5599656 4.723219 4.1629553 4.053813 4.524928 6.371196
o3_conc: 69.35357 70.81811 71.61889 71.439384 70.99925 70.05165
pm10_conc: 11.600811 11.010193 10.444889 10.026692 9.667715 9.815989
pm2p5_conc: 11.315586 10.734458 10.171167 9.751464 9.406523 9.551438
```

## Developper notes

### Why the netcdf format instead of grib ?

Originally, the Java app was supposed to extract data from GRIB files. However, the GRIB files downloaded from Copernicus used a specific template 40 which isn't handled by ucar's grib library (and thus geotools, which is based on it).

The eccodes library would work, as they are the ones that provide the downloads, but you would need to install the C++ library as well, which is not possible for us.
