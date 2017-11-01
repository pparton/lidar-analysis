"""
Script to create sky model hillshades based on Kennelly and Patrick (2014)
On the to do list:
1. Set a nodata mask in the numpy array to avoid the infinite numbers it currently creates DONE
2. Sort out the iterator so that we can create the multiple hillshades from different angles DONE
3. Create a function to sum all the hillshades and create a final, weighted hillshade DONE
4. Can we tile the tiffs for cloud compatibility>
5. Can we make it faster and/or capable of optimisations for really large tiffs?
"""

import rasterio
import numpy as np
import csv

inDem = "Hammond_Island_2011_Is_1m.tif"
parameters = 'model_overcast.txt'

# Import the DEM to the model
with rasterio.open(inDem) as src:
    np.seterr(divide='ignore', invalid='ignore', over='ignore') # set numpy error ignores - is this necessary now masked = true?
    timesDem = (src.read(1, masked = True))*5 # Read the elevation band and tell numpy nodata should not be calculated

# Function to load parameter file created from Kennelly and Patrick (2014) program
def csvIterator():
    print "Starting CSV iterator"
    with open('model_overcast.txt', 'r') as inFile:
        reader = csv.reader(inFile, delimiter=",")
        myList = list(reader)
        return myList

# Function to read HS parameters, calc HS, and write HS to a file
def doStufFunction(inDem, parameters):
    print "Doing the stuff"
    count = 0
    fileList = [] # A list for storing output filenames

    for line in parameters: # Iterate through
        az = float(line[0])
        alt = float(line[1])
        w = float(line[2])

        # The HS calculations
        x, y = np.gradient(inDem)
        slope = np.pi/2. - np.arctan(np.sqrt(x*x + y*y))
        aspect = np.arctan2(-x, y)
        azRad = az*np.pi/180.
        altRad = alt*np.pi/180.
        shaded = w*(255*(np.sin(altRad)*np.sin(slope) + np.cos(altRad)*np.cos(slope)*np.cos((azRad - np.pi/2.) - aspect))/2)

        count += 1
        fileList.append('hs'+str(int(az))+'_'+str(int(alt))+'.tif') # Add filename string to list

        # Set the spatial extents of out image to mirror the input
        kwargs = src.meta
        kwargs.update(dtype=rasterio.float32, count = 1)

        # Save the HS
        with rasterio.open('hs'+str(int(az))+'_'+str(int(alt))+'.tif', 'w', **kwargs) as dst:
            dst.write_band(1, shaded.astype(rasterio.float32))
            dst.close()
            print "Finished " + str(count)

    return fileList

# A function for summing the weighted rasters to create final model
def addRasters(origDem, processedHs):
    print "Starting add rasters"
    zeroDem = origDem * 0
    count = 0

    # Iterate and add the rasters the rasters
    for line in processedHs:
        with rasterio.open(line) as inFile:
            weightedHs = inFile.read(1, masked = True)
        if count == 0:
            sumRaster = np.add(weightedHs, zeroDem)

            print "Merging started"
        else:
            sumRaster = np.add(weightedHs, sumRaster)
            print "Adding " + str(count)

        count += 1

    # Set the spatial extents of out image to mirror the input
    kwargs = inFile.meta
    kwargs.update(dtype=rasterio.float32, count = 1)

    # Save the HS
    with rasterio.open(inDem[:-4] + "_" + parameters[:-4] + '.tif','w',**kwargs) as dst:
        dst.write_band(1, sumRaster.astype(rasterio.float32))
        dst.close()
        print "Finished"

# Main function
def main():
    mainList = csvIterator()
    outputFileList = doStufFunction(timesDem, mainList)
    addRasters(timesDem, outputFileList)

main()
