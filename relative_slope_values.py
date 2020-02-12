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
'''

datalist=glob.glob('/net/tiampostorage/volume1/MyleneShare/Bigsur_asc/az1rng2/amplitude/*.tif')
slidepolygon='/home/myja3483/Landslides/Bigsur/QGIS/slide_outlineWGS84.shp'
refpolygon='/home/myja3483/Landslides/Bigsur/QGIS/ref_slopeWGS84.shp'

values = pd.DataFrame(columns=["date","slide_median","slide_mean","ref_median","ref_mean"])
for fn in datalist:
    temp=pd.DataFrame(columns=["date","slide_median", "slide_mean","ref_median","ref_mean"])
    tif=ntpath.basename(fn)
    slidestats=zonal_stats(slidepolygon,tif, stats="mean median")
    refstats=zonal_stats(refpolygon,tif,stats="mean median")
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

#plt.plot_date(values.date,mean,'o')
#plt.xlabel("Time")
#plt.ylabel("Ratio")
#plt.show()

with open('asc_rel_amplitude.csv','w') as resultFile:
    wr=csv.writer(resultFile)
    wr.writerows(zip(values.date,median,mean))
