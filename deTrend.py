# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 12:26:03 2017

@author: partonpa
"""

import rasterio
from scipy.signal import medfilt

inDem = "Coconut_Island_2011_Is_1m.tif"
radius = 11

with rasterio.open(inDem) as src:
    array = src.read(1, masked = True)

filtered = medfilt(array, (radius, radius)).astype(rasterio.float32)
detrend = array - filtered

kwargs = src.meta
kwargs.update(dtype=rasterio.float32, count =1)

with rasterio.open(inDem[:-4] + "_" + "deTrend" + "_" + "rad" + str(radius) + ".tif", "w", **kwargs) as dst:
    dst.write_band(1, detrend.astype(rasterio.float32))
    dst.close()

print("`osi")
