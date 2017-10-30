"""
Script to create sky model hillshades
On the to do list 1. set a nodata mask in the numpy array to avoid the infinite numbers it currently creates
2. sort out the iterator so that we can create the multiple hillshades from different angles
3. create a function to sum all the hillshades and create a final, weighted hillshade
"""

import rasterio
import numpy as np
import csv

inDem = "coco.tif"
parameters = 'model_overcast.txt'

with rasterio.open(inDem) as src:
    np.seterr(divide='ignore', invalid='ignore', over='ignore')
    timesDem = (src.read(1))*5

def doStufFunction(inDem):
#np.seterr(divide='ignore', invalid='ignore', over='ignore')
#array * 5
    az = 315.
    alt = 45.
    w = 1.
    x, y = np.gradient(inDem)
    slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
    aspect = np.arctan2(-x, y)
    azRad = az*np.pi/180.
    altRad = alt*np.pi/180.
    shaded = w*(np.sin(altRad)*np.sin(slope) + np.cos(altRad)*np.cos(slope)*np.cos((azRad - np.pi/2.) - aspect))

    kwargs = src.meta
    kwargs.update(dtype=rasterio.float32, count = 1)

    with rasterio.open('hs'+str(int(az))+'_'+str(int(alt))+'.tif', 'w', **kwargs) as dst:
        dst.write_band(1, shaded.astype(rasterio.float32))
        dst.close()
        print "Done"

#Working on setting a nodata mask on the input array so that calcs aren't performed on nodata pixels
"""
def csvIterator():
    with open('model_overcast.txt', 'r') as in_file:
        reader = csv.reader(in_file)
        for line in reader:
            az = float(line[0])
            alt = float(line[1])
            w = float(line[2])
            #print az, alt, w
        return az, alt, w
"""
def main():
    #mainList = csvIterator()
    doStufFunction(timesDem)

main()
