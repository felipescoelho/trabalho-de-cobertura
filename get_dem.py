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

# Creatinfg exception for taking too many tiles:
if lat_dif >= 2 or lon_dif >= 2:
    raise Exception('Os pontos estão muito distantes, tente aproximá-los.\n\n\
Sugere-se uma distância de não mais de 10° entre pontos de um mesmo eixo.\n')

lat_aux = 0
lon_aux = 0
if lat_dif != 0:
    lat_aux = np.zeros(lat_dif+1, dtype=int)
    for i in np.arange(north, south+1):
        lat_aux[i-north] = i
if lon_dif != 0:
    lon_aux = np.zeros(lon_dif+1, dtype=int)
    for i in np.arange(west, east+1):
        lon_aux[i-west] = i

# Creating lists of needed tiles and Downloading them:
url_list = []
cache_list = []
if lat_dif != 0 and lon_dif != 0:
    for i in range(lon_dif+1):
        for j in range(lat_dif+1):
            url_list.append([url_path + 'srtm_{}_{}.zip'.format(lon_aux[i],
                            lat_aux[j])])
            cache_list.append([cache_path + 'srtm_{}_{}.zip'
                              .format(lon_aux[i], lat_aux[j])])
elif lat_dif != 0 and lon_dif == 0:
    for i in range(lat_dif+1):
        url_list.append([url_path + 'srtm_{}_{}.zip'.format(south,
                        lat_aux[i])])
        cache_list.append([cache_path + 'srtm_{}_{}.zip'
                          .format(south, lat_aux[i])])
elif lon_dif != 0 and lat_dif == 0:
    for i in range(lon_dif+1):
        url_list.append([url_path + 'srtm_{}_{}.zip'.format(lon_dif[i],
                        east)])
        cache_list.append([cache_path + 'srtm_{}_{}.zip'.format(lon_dif[i],
                          east)])
else:
    url_list.append([url_path + 'srtm_{}_{}.zip'.format(south, east)])
    cache_list.append([url_path + 'srtm_{}_{}.zip'.format(south, east)])

print(lat_aux)
print(lat_dif)
print(lon_aux)
print(lon_dif)
print(north, west, south, east)
print(cache_list)
