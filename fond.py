#!/usr/bin/env python3

# Uses Copernicus Climate Change Service information 2020
# (as per their license ?)

import cdsapi

c = cdsapi.Client()

c.retrieve(
    'cams-europe-air-quality-forecasts',
    {
        'model': 'chimere',
        'date': '2020-12-08/2020-12-08',
        'format': 'grib',
        'type': 'forecast',
        'time': '00:00',
        'variable': [
            'nitrogen_dioxide', 'ozone', 'particulate_matter_10um',
            'particulate_matter_2.5um',
        ],
        'level': '0',
        'leadtime_hour': [
            '0', '1', '2',
            '3', '4', '5',
            '6',
        ],
        'area': [
            47.66, -2.08, 46.9,
            -0.69,
        ],
    },
    'download.grib')