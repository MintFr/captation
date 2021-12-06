import pandas as pd
import logging
import sys

def main(pathCapteur, pathWeather, outputFileName="res"):
    """
    Data from capteur 

    """

    # Logger to get info in the terminal
    logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.DEBUG)
    logging.info('Launching merge')

    # Importing data from the capteur
    dfCapteur = pd.read_csv(pathCapteur, skiprows=4, delimiter='\t', skipfooter=1, engine='python')
    # dropping an unused column
    dfCapteur.drop('Unnamed: 9', axis = 1, inplace=True)

    # Importing data from weather
    dfWeather = pd.read_csv(pathWeather, skiprows=14, delimiter=';', header=0)
    # Remove space at the end of heure
    dfWeather['heure'] = dfWeather['heure'].apply(lambda x: x.strip())

    # Creation of the final dataset, merge on hour of the data
    dfFinal = dfWeather.merge(how='inner', right=dfCapteur, left_on='heure', right_on='time beginning', )

    # Filling the data of exposition
    dfFinal['PM1[µm)'] = dfFinal['PM1_classic - ']
    dfFinal['PM2.5[µm)'] = dfFinal['PM2.5_classic - ']
    dfFinal['PM4[µm)'] = dfFinal['PM4_classic - ']
    dfFinal['PMTot[µm)'] = dfFinal['PMtotal_classic - ']
    dfFinal.drop(['PM1_classic - ', 'PM2.5_classic - ', 'PM4_classic - ', 'PMtotal_classic - '], axis = 1, inplace=True)

    logging.info(f'Data wrote in {outputFileName}.csv')
    # Write it in a csv file
    dfFinal.to_csv(f'{outputFileName}.csv', sep='\t')

    logging.info('Done, thank you pole dev !!')

    return 0

if __name__ == "__main__":
    print("Launching script " + sys.argv[0])
    main(sys.argv[1], sys.argv[2], sys.argv[3])