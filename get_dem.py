# -*- coding: utf-8 -*-

# ALuno: Luiz Felipe da S. Coelho
# filename: get_dem.py

from math import ceil
import numpy as np
import wget
import os
import pathlib
import zipfile


url_path = 'http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/'
cache_path = './cache/'

print("Digite as coordenadas da antena transmissora:\n\n\
      (Coloque os valores no formato LATITUDE LONGITUDE)\n\
      (Não precisa de vírgula para separar os valores e casas decimais são\
      definidas por ponto.")
tx_aux = (input()).split(' ')

print("Digite as coordenadas da antena receptora:\n\n\
      (Coloque os valores no formato LATITUDE LONGITUDE)\n\
      (Não precisa de vírgula para separar os valores e casas decimais são\
      definidas por ponto.")
rx_aux = (input()).split(' ')

rx_coord = np.zeros((2,))
tx_coord = np.zeros((2,))
for i in range(2):
    tx_coord[i] = tx_aux[i]
    rx_coord[i] = rx_aux[i]

# Organizing LAT LON parameters:
if tx_coord[0] > rx_coord[0]:  # NORTH > SOUTH
    north = tx_coord[0]
    south = rx_coord[0]
else:
    north = rx_coord[0]
    south = tx_coord[0]
if tx_coord[1] > rx_coord[1]:  # EAST > WEST
    east = tx_coord[1]
    west = rx_coord[1]
else:
    east = rx_coord[1]
    west = tx_coord[1]

bounds = (north, west, south, east)  # bounds = (NORTH, WEST, SOUTH, EAST)

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

# Creating lists of needed tiles:
# creating directory for downloaded data
pathlib.Path('./cache/zip/').mkdir(parents=True, exist_ok=True)
url_list = []
cache_list = []
if lat_dif != 0 and lon_dif != 0:  # getting many tiles in both directions
    for i in range(lon_dif+1):
        for j in range(lat_dif+1):
            url_list.append([url_path + 'srtm_{}_{}.zip'.format(lon_aux[i],
                            lat_aux[j])])
            cache_list.append(['./cache/zip/srtm_{}_{}.zip'
                              .format(lon_aux[i], lat_aux[j])])
elif lat_dif != 0 and lon_dif == 0:  # getting many tiles in different lat
    for i in range(lat_dif+1):
        url_list.append([url_path + 'srtm_{}_{}.zip'.format(east,
                        lat_aux[i])])
        cache_list.append(['./cache/zip/srtm_{}_{}.zip'
                          .format(east, lat_aux[i])])
elif lon_dif != 0 and lat_dif == 0:  # getting many tiles in different long
    for i in range(lon_dif+1):
        url_list.append([url_path + 'srtm_{}_{}.zip'.format(lon_dif[i],
                        south)])
        cache_list.append(['./cache/zip/srtm_{}_{}.zip'.format(lon_dif[i],
                          south)])
else:
    url_list.append(url_path + 'srtm_{}_{}.zip'.format(east, south))
    cache_list.append('./cache/zip/srtm_{}_{}.zip'.format(east, south))

# Downloads:
for i in cache_list:
    exists = os.path.isfile(i)
    if exists:
        pass
    else:
        j = cache_list.index(i)
        wget.download(url_list[j], i)

# Extracting files:
filename_list = []
for i in cache_list:
    zip_ref = zipfile.ZipFile(i, 'r')
    # with zipfile.ZipFile(i, 'r') as file:
    zip_ref.extract(i[-14:-4] + '.tif', './cache/')
    zip_ref.close()
    filename_list.append(i[-14:-4] + '.tif')
