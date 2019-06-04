# -*- coding: utf-8 -*-

# ALuno: Luiz Felipe da S. Coelho
# filename: get_dem.py

from math import ceil
import numpy as np
import os

url_path = 'http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/'
cache_path = './cache/'

bounds = (45, -23, -38, -18)  # bounds = (NORTH, WEST, SOUTH, EAST)

# Setting valeus for those of the map:
north = abs(ceil((bounds[0]-60)/5))
west = abs(ceil((bounds[1]+180)/5))
south = abs(ceil((bounds[2]-60)/5))
east = abs(ceil((bounds[3]+180)/5))
if north == 0:
    north = 1
if west == 0:
    west = 1

# Need more than one map tile?
lat_dif = south-north
lon_dif = east-west
lat_aux = 0
lon_aux = 0

if lat_dif != 0:
    lat_aux = np.zeros(lat_dif, dtype=int)
    for i in np.arange(north, south):
        lat_aux[i-north] = i
if lon_dif != 0:
    lon_aux = np.zeros(lon_dif, dtype=int)
    for i in np.arange(west, east):
        lon_aux[i-west] = i

# Creating list of file names:
if lat_dif != 0 and lon_dif != 0:
    file_name = []
    for i in range(lon_dif):
        for j in range(lat_dif):
            file_name.append(['srtm_{}_{}.zip'.format(lon_aux[i], lat_aux[j])])

print(lat_aux)
print(lon_aux)
print(north, west, south, east)
print(file_name)
