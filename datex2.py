#!/usr/bin/env python3

import argparse
import configparser
import sys
import csv
import re
import os
import xml.etree.ElementTree as ET
from datetime import datetime

import requests

# TODO what is DataTRT (vs. DataTR)


# Utility
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def download_latest_data(auth):
    """
    Find the latest Datex2 xml file by navigating the index.
    Returns the filename
    """
    nantes_url = "http://diffusion-numerique.info-routiere.gouv.fr/tipitrafic/TraficBreizhNantes/"

    # Fetch index page and find the latest folder
    r = requests.get(nantes_url, auth = auth)
    r.raise_for_status()
    last_folder = re.findall("\d{4}-\d{2}-\d{2}_\d{2}/", r.text)[-1]

    # Fetch folder page and find the latest XML file
    print("GET …/%s" % last_folder)
    hour_folder_url = nantes_url + last_folder
    r = requests.get(hour_folder_url, auth = auth)
    r.raise_for_status()
    last_file = re.findall("TraficBreizhNantes_1_DataTR_\d{8}_\d{6}.xml", r.text)[-1]
    # last_file will also be the filename

    # Download file
    print("GET …/%s" % last_file)
    file_url = hour_folder_url + last_file
    r = requests.get(file_url, auth = auth)
    r.raise_for_status()
    with open(last_file, 'wb') as f:
        f.write(r.content)
    
    return last_file

def parse_xml_file(filename):
    """
    Parses the Datex2 xml file, and returns a list of csv rows, including header
    """

    # XML namespaces because ElementTree parses child elements of d2LogicalModel namespaced
    ns = {
        'd2': "http://datex2.eu/schema/2/2_0",
        'xsi': "http://www.w3.org/2001/XMLSchema-instance"
    }
    tree = ET.parse(filename)
    root = tree.getroot()

    data = []
    for m in root.findall('d2:payloadPublication/d2:siteMeasurements', ns):
        siteId = m.find('d2:measurementSiteReference', ns).get('id')
        time = m.find('d2:measurementTimeDefault', ns).text

        row = [siteId, time]
        # This would work, but ElementTree doesn't support `*[position]` selectors
        #m.findall('d2:measuredValue/d2:measuredValue/d2:basicData/*[2]/*[1]', ns)
        items = 3 # The number of values to insert
        for basicData in m.findall('d2:measuredValue/d2:measuredValue/d2:basicData', ns):
            # Print the data's label (unneeded)
            datatype = basicData.get('{%s}type' % ns['xsi'])

            value = basicData[1][0].text
            nbInputValues = basicData[1].get("numberOfInputValuesUsed")

            row.append(value)
            items = items - 1
        
        # Insert None for the missing columns
        # This is to fix the line with MWN44.B1, which happens to not have a TrafficSpeed entry ?
        for i in range(items):
            row.append(None)
        
        row.append(nbInputValues)

        data.append(row)

    header = ["measurementSiteReference", "measurementTimeDefault", "TrafficFlow", "TrafficConcentration", "TrafficSpeed", "numberOfInputValuesUsed"]
    data.insert(0, header)

    return data


def main(configfile = None, outputfile = None):
    # Argument defaults
    if configfile is None:
        configfile = "config.ini"

    # Read configuration
    config = configparser.ConfigParser()
    config.read(configfile)

    auth = (config['tipitrafic']['username'], config['tipitrafic']['password'])

    # Handle invalid configuration values
    if re.fullmatch('[A-Z_]+', auth[0]): # eg. 'TIPI_USERNAME'
        raise ValueError("Missing tipitrafic username")
    if re.fullmatch('[A-Z_]+', auth[1]): # eg. 'TIPI_USERNAME'
        raise ValueError("Missing tipitrafic password")


    # Download data and parse it
    filename = download_latest_data(auth)
    data = parse_xml_file(filename)

    # Delete downloaded file
    os.unlink(filename)

    # Write CSV data
    if outputfile is not None:
        with open(outputfile, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(data)
    else:
        writer = csv.writer(sys.stdout)
        writer.writerows(data)

    # Return data time
    timestamp = data[1][1]
    # Remove colon in UTC offset (eg. `+01:00`) so that it works in Python < 3.7
    timestamp = re.sub(r'(\+\d{2}):', r'\1', timestamp)
    dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
    return dt


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help = "Output file")
    parser.add_argument("--config")
    args = parser.parse_args()

    main(configfile = args.config, outputfile = args.file)
