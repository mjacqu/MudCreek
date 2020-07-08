#!/usr/bin/python3
import os
import glob
from rasterstats import zonal_stats
import pandas as pd
import matplotlib.dates as mdates
import ntpath
import re


# save results to:
resultpath = '/home/myja3483/Landslides/Bigsur/Results'

#NDVI datasets (UTM)
ndvi_datapath='/home/myja3483/Landslides/Bigsur/NDVI/'
ndvi_slidepoly='/home/myja3483/Landslides/Bigsur/QGIS/slide_outline.shp'
ndvi_refpoly='/home/myja3483/Landslides/Bigsur/QGIS/ref_slope.shp'
ndvi_name = 'NDVI'

#radar datasets (WGS84)
radar_datapath=('/net/tiampostorage/volume1/MyleneShare/Bigsur_desc/az1rng2/coherence', #descending coherence
'/net/tiampostorage/volume1/MyleneShare/Bigsur_desc/az1rng2/amplitude', #descending amplitude
'/net/tiampostorage/volume1/MyleneShare/Bigsur_asc/az1rng2/coherence', #ascending coherence
'/net/tiampostorage/volume1/MyleneShare/Bigsur_asc/az1rng2/amplitude') #ascending amplitude
radar_slidepoly='/home/myja3483/Landslides/Bigsur/QGIS/slide_outlineWGS84.shp'
radar_refpoly='/home/myja3483/Landslides/Bigsur/QGIS/ref_slopeWGS84.shp'
radar_name = ('desc_coh', 'desc_amp', 'asc_coh', 'asc_amp')

def compute_relative_values(path, slidepoly, refpoly, resultpath, name):
    '''
    Compute ratio beetween mean raster values inside one polygon and average value in another polygon.

    Parameters:
    path (str): path to directory with ndvi, coherence, or amplitude tiff auxfiles
    slidepoly (str): path to geojson or shape file of slide outline
    refpoly (str): path to geojson or shape file of reference area outline
    resultpath (str:) path for saving results files
    name (str): file name for result output

    Returns:
    values (DataFrame): Pandas dataframe with dates mean and median of the reference slope,
                        the slide polygon, and the ratio between the two.
    '''
    values = pd.DataFrame(columns=["date","slide_median","slide_mean","ref_median","ref_mean"])
    datalist = glob.glob(os.path.join(path, '*.tif'))
    for fn in datalist:
        temp=pd.DataFrame(columns=["date","slide_median", "slide_mean","ref_median","ref_mean"])
        tif=ntpath.basename(fn)
        slidestats=zonal_stats(slidepoly,fn, stats="mean median")
        refstats=zonal_stats(refpoly,fn,stats="mean median")
        regex = re.compile(r'\d{8}')
        datestrings = regex.findall(tif)
        if len(datestrings) == 2:
            startdate = mdates.date2num([pd.to_datetime(datestrings[0],format = '%Y%m%d')])
            enddate = mdates.date2num([pd.to_datetime(datestrings[1],format = '%Y%m%d')])
            temp["date"] = mdates.num2date((startdate + enddate)/2)
        if len(datestrings) == 1:
            temp["date"] = [pd.to_datetime(datestrings[0],format = '%Y%m%d')]
        temp["slide_median"]=[d["median"] for d in slidestats]
        temp["slide_mean"]=[d["mean"] for d in slidestats]
        temp["ref_median"]=[d["median"] for d in refstats]
        temp["ref_mean"]=[d["mean"] for d in refstats]
        values=values.append(temp)
    values['rel_median']=values.slide_median.divide(values.ref_median)
    values['rel_mean']=values.slide_mean.divide(values.ref_mean)
    values = values.sort_values(by = ["date"])
    values.to_csv(os.path.join(resultpath, name)+ '.csv', index = False)
    return values

values = compute_relative_values(ndvi_datapath, ndvi_slidepoly, ndvi_refpoly, resultpath, ndvi_name)

for d,n in zip(radar_datapath,radar_name):
    compute_relative_values(d, radar_slidepoly, radar_refpoly, resultpath, n)
