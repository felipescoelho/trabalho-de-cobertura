# -*- coding utf-8 -*-

# Author: Luiz Felipe Coelho, lfscoelho@ieee.org
# filename: profile2.py

import rasterio
import math


# Haversine function:
def haversine(lat1, lon1, lat2, lon2):
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    a = math.sqrt((math.sin(delta_lat/2))**2 + math.cos(lat1_rad) *
                  math.cos(lat2_rad)*(math.sin(delta_lon/2))**2)
    d = 2*637100*math.asin(a)
    return d

# Open clipped GeoTIFF, using rasterio:
geotiff = 'clipped.tif'

data = rasterio.open(geotiff)
nodatavals = data.get_nodatavals()
data_array = data.read(1)

