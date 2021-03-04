#!/usr/bin/env python3

import netCDF4 as netcdf

filename = 'Conc_NO2_2014010101.nc'

netdata = netcdf.Dataset(filename)

print(netdata)

c = netdata['Conc']

print(c.ncattrs())
print(c.get_dims())

print(c[1:5, 1:5])