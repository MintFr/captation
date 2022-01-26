import pandas as pd
import geopandas as gpd
import logging
import sys
from gpx_converter import Converter

def main(filename):


    # Logger to get info in the terminal
    logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.DEBUG)
    logging.info('Launching merge')

    for fil in filename:
        df = Converter(input_file='SO_25-01-22_Pied_3_Aller_Geoloc.gpx').gpx_to_dataframe()
        gdf = gpd.read_file(fil)
        gdf['lat'] = gdf.geometry.y
        gdf['lon'] = gdf.geometry.x

        df2 = df.merge(right=gdf[['name', 'lat', 'lon']], how='left', left_on=['latitude', 'longitude'], right_on=['lat', 'lon']).drop_duplicates()

        df2.drop(['lon', 'lat'], axis=1, inplace=True)

        df2.to_csv(f"datagpxtocsv/{fil[:-3]}csv", index=False)

if __name__ == "__main__":
    print("Launching script" + sys.argv[0])
    main((sys.argv[1:]))



