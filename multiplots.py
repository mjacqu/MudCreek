#from __future__ import division
import os
#import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
#import matplotlib.image as mpimg
#import shapefile
#import math
import glob
from shapely.geometry.polygon import Polygon
import re
import geopandas as gpd
from rasterstats import zonal_stats
#from isce2world import ENVI_raster_binary_to_2d_array
#from osgeo import gdal, gdalconst
from osgeo import gdal_array
#from osgeo.gdalconst import *
#import json
#from shapely.geometry import shape, GeometryCollection


# Import data and set parameters
# define extent of radar data in map coordinates
radar_extent = [-121.5001,-121.3209, 35.7622, 35.9909] #min_lon, #max_lon, min_lat, max_lat
zoom_window = [-121.446, -121.403, 35.885, 35.8459]
##################################################
# define landslide polygon (mapped from coherence)
##################################################
#landslide_loc = Polygon(
#	[(-121.433,35.8653),(-121.432,35.865),(-121.431,35.864),(-121.429,35.8636),
#	(-121.427,35.8649),(-121.426,35.8658),(-121.426,35.8666),(-121.425,35.8671),
#	(-121.425,35.8681),(-121.427,35.868),(-121.428,35.8676),(-121.43,35.8688),
#	(-121.433,35.8671),(-121.434,35.8661)])

#gpd.GeoSeries([landslide_loc]).to_file('coherence_mpd_slide_outline.geojson', driver = 'GeoJSON') #write out to geojson

ref_slope_large = gpd.read_file("/home/myja3483/isce_tools/MudCreek/ref_slope_large.geojson")
slide_outline = gpd.read_file("/home/myja3483/isce_tools/MudCreek/slide_outline.geojson")
coast = gpd.read_file("/home/myja3483/isce_tools/MudCreek/california.geojson")


# LOAD COHERENCE FILES + MAKE 3D NUMPY ARRAY
# coh_files = glob.glob('/home/myja3483/Landslides/Bigsur/highres/coherence/*.coh.geo')
title = 'Effective Coherence (1az2rng)'
fullfn = 'Effective_coh_medres_all'
zoomfn = 'asc_low'
cscale = (0,1)

path= '/net/tiampostorage/volume1/MyleneShare/Bigsur_asc/low_coherence_az1rng2'

coh_files = glob.glob(os.path.join(path, '*coherence.tif'))
r = re.compile('([0-9]+?)_[0-9]+?.')
def key_func(m):
	return int(r.search(m).group(1))


coh_files = sorted(coh_files, key=key_func)
coh_3darray= np.zeros((2471,1936,len(coh_files)))

for i in range (0, len(coh_files)):
	coherence_array = gdal_array.LoadFile(coh_files[i])
	coh_3darray[:,:,i] = coherence_array

coh_stats = [zonal_stats('/home/myja3483/isce_tools/MudCreek/ref_slope_large.geojson', i) for i in coh_files]
coh_means = [d[0]["mean"] for d in coh_stats]
#############################
# 2. zoom plots on slide
############################
for j in range (0,18):
	fig = plt.figure(figsize=(18,10))  # width, height in inches
	for i in range(0,8):
		sub = fig.add_subplot(2, 4, i+1)
		cmap = matplotlib.cm.binary_r
		# cmap.set_bad(color='black')
		im = sub.imshow(coh_3darray[:,:,i+8*j],extent=radar_extent, clim=cscale, cmap=cmap)
		plt.xlim(zoom_window[0],zoom_window[1])
		plt.ylim(zoom_window[3],zoom_window[2])
		gpd.plotting.plot_dataframe(ref_slope_large.boundary, color = 'b', ax = sub)
		gpd.plotting.plot_dataframe(slide_outline.boundary, color = 'r', ax = sub)
		gpd.plotting.plot_dataframe(coast.boundary, color = 'k', ax = sub)
		#plt.plot(a,b,'k') # plot landslide polygon
		[first,second] = coh_files[i+8*j].replace(path,'').split("_") # ugly hack to get dates for title
		#plt.title(first,y=1.08)
		plt.title(str(round(coh_means[i+8*j],2))+'\n'+str(first[1:])+'_'+str(second[0:8])) #uglier hack to plot title
		#plt.title(os.path.basename(coh_files[i+8*j]))
		#for shape in cali_coast.shapeRecords():
		#	s1 = [i[0] for i in shape.shape.points[:]]
		#	s2 = [i[1] for i in shape.shape.points[:]]
		#	plt.plot(s1,s2,'-k')
	fig.subplots_adjust(right=0.87)
	cbar_ax = fig.add_axes([0.9, 0.35, 0.02, 0.3])
	fig.colorbar(im, cax=cbar_ax)
	fig.suptitle(title, y=0.975, fontsize=20)
	fig.savefig(zoomfn+str(j)+'.pdf')
	#plt.show()



'''

#############################
# 1. full plots (no zoom)
############################
for j in range (0,15):
	fig = plt.figure(figsize=(18,10))  # width, height in inches
	for i in range(0,8):
		sub = fig.add_subplot(2, 4, i+1)
		cmap = matplotlib.cm.jet
		# cmap.set_bad(color='black')
		im = sub.imshow(coh_3darray[:,:,i+8*j],extent=radar_extent, clim=cscale, cmap=cmap)
		plt.xlim(radar_extent[0],radar_extent[1])
		plt.ylim(radar_extent[2],radar_extent[3])
		plt.plot(a,b,'k') # plot landslide polygon
		[first,second,bla]=coh_files[i+8*j].replace('/mnt/MyleneShare/Bigsur_desc/coherence/','').split("_")
		plt.title(first+"_"+second,y=1)
		# for shape in cali_coast.shapeRecords():
		# 	s1 = [i[0] for i in shape.shape.points[:]]
		# 	s2 = [i[1] for i in shape.shape.points[:]]
		# 	plt.plot(s1,s2,'-k')
	fig.subplots_adjust(right=0.87)
	cbar_ax = fig.add_axes([0.9, 0.35, 0.02, 0.3])
	fig.colorbar(im, cax=cbar_ax)
	fig.suptitle(title, y=0.975, fontsize=20)
	# fig.savefig(fullfn+str(j)+'.png')

plt.show()

#####################
# last plot with 4 figures (no zoom)
#####################
fig = plt.figure(figsize=(18,5))  # width, height in inches
fig.subplots_adjust(right=0.87)
cbar_ax = fig.add_axes([0.9, 0.35, 0.02, 0.3])
fig.colorbar(im, cax=cbar_ax)
fig.suptitle(title, y=0.975, fontsize=20)
for i in range(0,4):
	sub = fig.add_subplot(1, 4, i+1)
	cmap = matplotlib.cm.jet
	# cmap.set_bad(color='black')
	im = sub.imshow(coh_3darray[:,:,144+i],extent=radar_extent, clim=cscale, cmap=cmap)
	plt.xlim(radar_extent[0],radar_extent[1])
	plt.ylim(radar_extent[2],radar_extent[3])
	plt.plot(a,b,'k') # plot landslide polygon
	[first,second,bla]=coh_files[144+i].replace('/mnt/MyleneShare/Bigsur_desc/coherence/','').split("_")
	plt.title(first+"_"+second,y=1)
	for shape in cali_coast.shapeRecords():
		s1 = [i[0] for i in shape.shape.points[:]]
		s2 = [i[1] for i in shape.shape.points[:]]
		plt.plot(s1,s2,'-k')

#fig.savefig(fullfn+'18.png')

plt.show()

#####################
# last plot with 4 figures (zoom)
#####################
fig = plt.figure(figsize=(18,5))  # width, height in inches
fig.subplots_adjust(right=0.87)
cbar_ax = fig.add_axes([0.9, 0.35, 0.02, 0.3])
fig.colorbar(im, cax=cbar_ax)
fig.suptitle(title, y=0.975, fontsize=20)
for i in range(0,4):
	sub = fig.add_subplot(1, 4, i+1)
	cmap = matplotlib.cm.jet
	# cmap.set_bad(color='black')
	im = sub.imshow(coh_3darray[:,:,144+i],extent=radar_extent, clim=cscale, cmap=cmap)
	plt.xlim(zoom_window[0],zoom_window[1])
	plt.ylim(zoom_window[3],zoom_window[2])
	plt.plot(a,b,'k') # plot landslide polygon
	[first,second,bla]=coh_files[144+i].replace('/mnt/MyleneShare/Bigsur_desc/coherence/','').split("_")
	plt.title(first+"_"+second,y=1.08)
	for shape in cali_coast.shapeRecords():
		s1 = [i[0] for i in shape.shape.points[:]]
		s2 = [i[1] for i in shape.shape.points[:]]
		plt.plot(s1,s2,'-k')

fig.savefig(zoomfn+'18.png')

# plt.show()
'''
