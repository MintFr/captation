#!/usr/bin/env python3

import argparse
import sys
import csv
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument("--xml")
parser.add_argument("--file", help = "Output file")
args = parser.parse_args()

ns = {
    'd2': "http://datex2.eu/schema/2/2_0",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}
tree = ET.parse(args.xml)
root = tree.getroot()

data = []
for m in root.findall('d2:payloadPublication/d2:siteMeasurements', ns):
    siteId = m.find('d2:measurementSiteReference', ns).get('id')
    time = m.find('d2:measurementTimeDefault', ns).text

    row = [siteId, time]
    # This would work, but ElementTree doesn't support `*[position]` selectors
    #m.findall('d2:measuredValue/d2:measuredValue/d2:basicData/*[2]/*[1]', ns)
    for basicData in m.findall('d2:measuredValue/d2:measuredValue/d2:basicData', ns):
        # Print the data's label (unneeded)
        #datatype = data.get('{%s}type' % ns['xsi'])
        #print(datatype)

        row.append(basicData[1][0].text)
    data.append(row)

header = ["measurementSiteReference", "measurementTimeDefault", "TrafficFlow", "TrafficConcentration", "TrafficSpeed"]
data.insert(0, header)

if args.file is not None:
    with open(args.file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)
else:
    writer = csv.writer(sys.stdout)
    writer.writerows(data)
