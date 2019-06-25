# -*- coding: utf-8 -*-

# ALuno: Luiz Felipe da S. Coelho
# filename: get_dem.py

from math import ceil
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import wget
import os
import gdal_merge
import pathlib
import zipfile
import rasterio
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg
import pycrs


url_path = 'http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/'
cache_path = './cache/'
out_tif = 'clipped.tif'

# print("Digite as coordenadas da antena transmissora:\n\n\
#       (Coloque os valores no formato LATITUDE LONGITUDE)\n\
#       (Não precisa de vírgula para separar os valores e casas decimais são\
#       definidas por ponto.")
# tx_aux = (input()).split(' ')

# print("Digite as coordenadas da antena receptora:\n\n\
#       (Coloque os valores no formato LATITUDE LONGITUDE)\n\
#       (Não precisa de vírgula para separar os valores e casas decimais são\
#       definidas por ponto.")
# rx_aux = (input()).split(' ')

# rx_coord = np.zeros((2,))
# tx_coord = np.zeros((2,))
# for i in range(2):
#     tx_coord[i] = tx_aux[i]
#     rx_coord[i] = rx_aux[i]

# # Organizing LAT LON parameters:
# if tx_coord[0] > rx_coord[0]:  # NORTH > SOUTH
#     north = tx_coord[0]
#     south = rx_coord[0]
# else:
#     north = rx_coord[0]
#     south = tx_coord[0]
# if tx_coord[1] > rx_coord[1]:  # EAST > WEST
#     east = tx_coord[1]
#     west = rx_coord[1]
# else:
#     east = rx_coord[1]
#     west = tx_coord[1]

# bounds = (north, west, south, east)
bounds = (-22.83, -43.31, -23.01, -43.05)

# Setting valeus for those of the map:
north = ceil(abs((bounds[0]-60)/5))
west = ceil(abs((bounds[1]+180)/5))
south = ceil(abs((bounds[2]-60)/5))
east = ceil(abs((bounds[3]+180)/5))
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
            url_list.append(url_path + 'srtm_{}_{}.zip'.format(lon_aux[i],
                            lat_aux[j]))
            cache_list.append('./cache/zip/srtm_{}_{}.zip'
                              .format(lon_aux[i], lat_aux[j]))
elif lat_dif != 0 and lon_dif == 0:  # getting many tiles in different lat
    for i in range(lat_dif+1):
        url_list.append(url_path + 'srtm_{}_{}.zip'.format(east,
                        lat_aux[i]))
        cache_list.append('./cache/zip/srtm_{}_{}.zip'
                          .format(east, lat_aux[i]))
elif lon_dif != 0 and lat_dif == 0:  # getting many tiles in different long
    for i in range(lon_dif+1):
        url_list.append(url_path + 'srtm_{}_{}.zip'.format(lon_aux[i],
                        south))
        cache_list.append('./cache/zip/srtm_{}_{}.zip'.format(lon_aux[i],
                          south))
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

# Creating a mosaic for case of more than one tile:
n_tiles = len(filename_list)
if n_tiles != 1:
    files_to_mosaic = []
    for i in filename_list:
        files_to_mosaic.append('cache/' + i)
    files_string = ' '.join(files_to_mosaic)
    command = " -o cache/sector.tif -of gtiff " + files_string
    gdal_merge.main(command.split(' '))
    data_file = 'cache/sector.tif'
else:
    data_file = 'cache/' + filename_list[0]

# Processing data:
# ----------------------------------------------------------------------------
# Open file GeoTIFF:

# data = gdal.Open(data_file)  # use GDAL to open the file and read as 2D array
# band = data.GetRasterBand(1)
# # getting NaN values:
# nodataval = band.GetNoDataValue()

# # Convert to a numpy array:
# data_array = data.ReadAsArray().astype(np.float)

# # Replace missing values if necessary:
# if np.any(data_array == nodataval):
#     data_array[data_array == nodataval] = np.nan
#     data_array = data_array[::-1]

# Mask data according to the antenna placement:
# ----------------------------------------------------------------------------

# open in raster read mode:
data = rasterio.open(data_file)

# plot the data:
# show((data, 1), cmap='gist_earth')

# creating a bounding box with shapely:
if bounds[0] > bounds[2]:
    lat1 = bounds[0] + .002  # adds approx. 220 m
    lat2 = bounds[2] - .002
else:
    lat1 = bounds[2] + .002
    lat2 = bounds[0] - .002
if bounds[1] > bounds[3]:
    lon1 = bounds[1] + .002
    lon2 = bounds[3] - .002
else:
    lon1 = bounds[3] + .002
    lon2 = bounds[1] - .002
minlon, minlat = lon2, lat2
maxlon, maxlat = lon1, lat1
bbox = box(minlon, minlat, maxlon, maxlat)

# insert bbox into a GeoDataFrame:
geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=from_epsg(4326))
# The Brazilian EPSG is different!

# reproject into the same coordinate system as raster data
geo = geo.to_crs(crs=data.crs.data)

# need to get the coordinates of the geometry in such a form that rasterio
# wants them:


def getFeatures(gdf):
    """ Function to parse features from GeoDataFrame in such a manner that
    rasterio want them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

# get the geometry coordinates by using the function:
coords = getFeatures(geo)
print(coords)

# Clip raster with the polygon using the 'coords' variable that was created.
# Clipping the raster can be done easily with the 'mask' function that was
# imported in the from 'rasterio', and specifying 'clip=True'.

out_img, out_transform = mask(data, shapes=coords, crop=True)

# Next modify the metadata. Start by coipying the metadata from the original
# data file.
# copy the metadata:
out_meta = data.meta.copy()
print(out_meta)

# Parse the EPSG value from the CRS so that a 'Proj4' string is created using
# the PyCRS library.

epsg_code = int(data.crs.data['init'][5:])
print(epsg_code)

# update the metadata with new dimensions, transform and CRS:
out_meta.update({'driver': 'GTiff', 'height': out_img.shape[1],
                 'width': out_img.shape[2], 'transform': out_transform,
                 'crs': pycrs.parse.from_epsg_code(epsg_code).to_proj4()})

# save the clipped raster to disk:
with rasterio.open(out_tif, 'w', **out_meta) as dest:
    dest.write(out_img)

clipped = rasterio.open(out_tif)
nodataval = clipped.get_nodatavals()
clipped_array = clipped.read(1)

# Visualize data with matplotlib:
# Plot out data with contour
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)
plt.contour(clipped_array[::-1], cmap='terrain', levels=list(range(-500,
            1200, 10)))
plt.title('Elevation Contours')
cbar = plt.colorbar()
plt.gca().set_aspect('equal', adjustable='box')

# Plot out data with contourf
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111)
plt.contourf(clipped_array[::-1], cmap='terrain', levels=list(range(-500,
             1200, 10)))
plt.title('Elevation Contours')
cbar = plt.colorbar()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()

# Getting Profile:
