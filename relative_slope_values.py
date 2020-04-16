#!/usr/bin/python3
import os
import glob
import six
from rasterstats import zonal_stats
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
import ntpath
import re

'''
Compute ratio beetween mean raster values inside one polygon and average value in another polygon.

Note: NDVI images are in UTM, isce outputs in WGS84. Use respective polygons.
'''
#NDVI datasets
datalist=glob.glob('/home/myja3483/Landslides/Bigsur/NDVI/NDVI_*.tif')
slidepolygon='/home/myja3483/Landslides/Bigsur/QGIS/slide_outline.shp'
refpolygon='/home/myja3483/Landslides/Bigsur/QGIS/ref_slope.shp'

#radar datasets
#datalist=glob.glob('/net/tiampostorage/volume1/MyleneShare/Bigsur_desc/az1rng2/coherence/*.tif') #descending coherence
datalist=glob.glob('/net/tiampostorage/volume1/MyleneShare/Bigsur_desc/az1rng2/amplitude/*.tif') #descending amplitude
#datalist=glob.glob('/net/tiampostorage/volume1/MyleneShare/Bigsur_asc/az1rng2/coherence/*.tif') #ascending coherence
#datalist=glob.glob('/net/tiampostorage/volume1/MyleneShare/Bigsur_asc/az1rng2/amplitude/*.tif') #ascending amplitude
slidepolygon='/home/myja3483/Landslides/Bigsur/QGIS/slide_outlineWGS84.shp'
refpolygon='/home/myja3483/Landslides/Bigsur/QGIS/ref_slopeWGS84.shp'

values = pd.DataFrame(columns=["date","slide_median","slide_mean","ref_median","ref_mean"])
for fn in datalist:
    temp=pd.DataFrame(columns=["date","slide_median", "slide_mean","ref_median","ref_mean"])
    tif=ntpath.basename(fn)
    slidestats=zonal_stats(slidepolygon,fn, stats="mean median")
    refstats=zonal_stats(refpolygon,fn,stats="mean median")
    regex = re.compile(r'\d{8}')
    datestrings = regex.findall(tif)
    if len(datestrings) == 2:
        startdate = mdates.date2num([pd.to_datetime(datestrings[0],format = '%Y%m%d')])
        enddate = mdates.date2num([pd.to_datetime(datestrings[1],format = '%Y%m%d')])
        temp["date"] = (startdate + enddate)/2
    if len(datestrings) == 1:
        temp["date"] = mdates.date2num([pd.to_datetime(datestrings[0],format = '%Y%m%d')])
    temp["slide_median"]=[d["median"] for d in slidestats]
    temp["slide_mean"]=[d["mean"] for d in slidestats]
    temp["ref_median"]=[d["median"] for d in refstats]
    temp["ref_mean"]=[d["mean"] for d in refstats]
    values=values.append(temp)


median=pd.DataFrame
mean=pd.DataFrame
median=values.slide_median.divide(values.ref_median)
mean=values.slide_mean.divide(values.ref_mean)

print(mean)
plt.plot_date(values.date,median,'o')
plt.xlabel("Time")
plt.ylabel("Ratio")
plt.show()


fig = plt.subplots(figsize = (10,4))
plt.plot_date(values.date, values.slide_mean, label='slide')
plt.plot_date(values.date, values.ref_mean, label='surrounding slope')
plt.legend()
plt.xlabel('Time')
plt.ylabel('NDVI')
plt.show()
#plt.savefig('NDVI_noratio.pdf')

'''
with open('NDVI.csv','w') as resultFile:
    wr=csv.writer(resultFile)
    wr.writerows(zip(values.date,median,mean))

'''

'''
with open('desc_rel_coherence_coh0.45.csv','w') as resultFile:
    wr=csv.writer(resultFile)
    wr.writerows(zip(values.date,median,mean))

'''
