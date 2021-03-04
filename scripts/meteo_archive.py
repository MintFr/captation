#!/usr/bin/env python3

import cdsapi

GRIB_RESOLUTION = 0.25

# NB hope that your square doesn't happen to overlap with the 0 meridian as it will not work properly
NANTES_COORD = [47.2172500, -1.5533600]

# Upper left, Lower right
area = [
    NANTES_COORD[0] + GRIB_RESOLUTION,
    NANTES_COORD[1] - GRIB_RESOLUTION,
    NANTES_COORD[0] - GRIB_RESOLUTION,
    NANTES_COORD[1] + GRIB_RESOLUTION,
]

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'format': 'grib',
        'variable': [
            '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_temperature',
            'total_cloud_cover', 'total_precipitation',
        ],
        'year': '2020',
        'month': '12',
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
        'area': area,
    },
    'download.grib')