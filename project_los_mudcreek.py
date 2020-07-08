import numpy as np
import sys
sys.path.append('/home/myja3483/isce_tools/GIANT')
import los_projection as lp
import importlib
import matplotlib.pyplot as plt
import glob
import gdal
import matplotlib.dates
import geopandas as gpd
import pandas as pd

#path to ISCE geometry file
los_rdr = '/net/tiampostorage/volume1/MyleneShare/Bigsur_desc/az1rng2/20170501_20170513/merged/los.rdr.geo'

#read los file to array
azimuth, incidence_angle = lp.read_los(los_rdr)

#rotate azimuth from counterclockwise from North to counterclockwise from East
azi_rot = lp.rotate_azimuth(azimuth.mean(), direction = 'cc')

#compute mean los vector from target to platform
target_to_platform = lp.pol2cart(azi_rot, incidence_angle.mean())

#reverse los vector to point from platform to target
p2t = lp.reverse_vector(target_to_platform)

#load aspect & slope file (WGS84, cropped to giant roi (min/max lat/long from below))
aspect_file = '/net/tiampostorage/volume1/MyleneShare/10mdem/AspectCrop.tif'
slope_file = '/net/tiampostorage/volume1/MyleneShare/10mdem/SlopeCrop.tif'

# load and smooth slope and aspect files
slope = lp.loadnfilter(slope_file, filter = 11)
aspect = lp.loadnfilter(aspect_file, filter = 11)

# rotate aspect from clockwise from North to counterclockwise from East
aspect_rotated = lp.rotate_azimuth(aspect)

# change slope from degrees from horizontal to degrees from vertical
vert_slope = lp.slope_from_vertical(slope)

# compute slope vectors for each pixel
slope_vectors = lp.pol2cart(aspect_rotated, vert_slope)

#compute angles between slope and line of sight (platform to target)
delta = lp.compute_delta(slope_vectors, p2t)

#load giant output (from text files for now, due to h5py issues)
filelist = glob.glob('/home/myja3483/Landslides/Bigsur/Results/Giant_desc/MudCreekRAWTS/20*.txt')
dates = np.loadtxt('/home/myja3483/Landslides/Bigsur/Results/Giant_desc/MudCreekRAWTS/dates.txt')
data = np.loadtxt(filelist[-1]) #[-1] bc 2015-03-25 is somehow broken?
all_data = [np.loadtxt(i) for i in filelist]
true_def = [lp.los2def(i, delta) for i in all_data]
true_def = np.dstack(true_def)


# plot time-series and total cumulative deformation:
# lat/long coordinates:
rdr_coor = [-121.5001,-121.3209, 35.7622, 35.9909] #from topsrun MUDCREEK (#min_lon, #max_lon, min_lat, max_lat)
zoom_window = [-121.446, -121.403, 35.885, 35.8459]
dims = [2471, 1936] # from run_giant [y, x]=[row, col] MUDCREEK
giant_roi = [640, 920, 1200, 1450] # from run_giant [col_min, col_max, row_min, row_max] MUDCREEK
########################################
radar_lats = np.arange(rdr_coor[3], rdr_coor[2], (rdr_coor[3]-rdr_coor[2])/-dims[0])
radar_lons = np.arange(rdr_coor[0], rdr_coor[1], (rdr_coor[1]-rdr_coor[0])/dims[1])[np.newaxis].T
lats = radar_lats[giant_roi[2]:giant_roi[3]]
lons = radar_lons[giant_roi[0]:giant_roi[1]][np.newaxis]

stable_area = [800, 1357]

# construct time series
pts = [[134, 118], [151, 126],[157, 128]]
timeseries = [true_def[group[0], group[1]] for group in pts]
#timeseries = np.abs(timeseries)

# turn displacements into velocities
m,n = 3,4
pt = [134, 118]
velocities = []

dD = np.diff(true_def)
#dV = [dD[group[0], group[1]] for group in pts]

for t in range(0, dD.shape[2]):
    slice = np.nanmean(dD[pt[0]-m:pt[0]+n,pt[1]-m:pt[1]+n,t])
    #slice = dD[pt[0],pt[1],t]
    velocities.append(slice)

dt = np.diff(dates)
mid_dates = []
for d in range(0, len(dates[:-1])):
    mid_date = dates[d]+dt[d]
    mid_dates.append(mid_date)

vel_year = pd.Series(velocities/dt)*365
rolling_vel = vel_year.rolling(window = 10)
mean = rolling_vel.mean()
#f2 = interp1d(mid_dates,mean)
plt.plot(matplotlib.dates.num2date(mid_dates),mean*-1, '.:',label = 'vel')
#xnew = np.linspace(mid_dates[0], mid_dates[-1], num=61, endpoint=True)
#plt.plot(matplotlib.dates.num2date(mid_dates), f2(xnew)*-1, '-')
#plt.plot(matplotlib.dates.num2date(dates[51:]), (1/mean[50:])*-1, label = 'inv')
plt.legend()
plt.show()

fig, ax = plt.subplots(figsize = (10,6))
plt.plot(matplotlib.dates.num2date(dates), timeseries[0]/-10, color = 'silver',
    marker = '*', mfc = 'k', mec = 'k', markersize = 6)#, label = str(pts[0]))
plt.plot(matplotlib.dates.num2date(dates), timeseries[1]/-10, color = 'silver',
    marker = 'x', mfc = 'k', mec = 'k', markersize = 6)#, label = str(pts[1]))
plt.plot(matplotlib.dates.num2date(dates), timeseries[2]/-10, color = 'silver',
    marker = '+', mfc = 'k', mec = 'k', markersize = 6)#, label = str(pts[2]))
plt.xlabel('Time')
plt.ylabel('Cumulative downslope displacement (cm)')
plt.title('Mud Creek landslide')
#plt.legend()
plt.show()
#plt.savefig('MudCreekTS.pdf')

#points in latlong:
pt_lats = [lats[group[0]] for group in pts]
pt_lons = [lons[:,group[1]] for group in pts]

#hillshade
#hs = gdal.Open('/net/tiampostorage/volume1/MyleneShare/10mdem/HillshadeCrop.tif')
#hillshade = hs.GetRasterBand(1).ReadAsArray()

slide_outline = gpd.read_file("/home/myja3483/isce_tools/MudCreek/slide_outline.geojson")
#coast = gpd.read_file("/home/myja3483/isce_tools/MudCreek/california.geojson")
moving = gpd.read_file("/home/myja3483/isce_tools/MudCreek/coherence_mpd_slide_outline.geojson")

fig, ax = plt.subplots(figsize = (10,10))
#lt.imshow(hillshade, cmap = 'Greys_r', extent = [lons.max(), lons.min(),lats.min(), lats.max()])
plt.imshow(true_def[:,:,-1]/10,vmin = -40, vmax = 0, cmap = 'OrRd_r',
    extent = [lons.min(), lons.max(), lats.min(), lats.max()], alpha = 0.9)
gpd.plotting.plot_dataframe(slide_outline.boundary, color = 'k', ax = ax)
#gpd.plotting.plot_dataframe(coast.boundary, color = 'k', ax = ax)
gpd.plotting.plot_dataframe(moving.boundary, color = 'k', ax = ax)
plt.plot(radar_lons[stable_area[0]],radar_lats[stable_area[1]], 'o')
plt.plot(pt_lons[0], pt_lats[0], 'k*')
plt.plot(pt_lons[1], pt_lats[1], 'kx')
plt.plot(pt_lons[2], pt_lats[2], 'k+')
ax.ticklabel_format(useOffset=False)
plt.xlim([-121.437, -121.422])
plt.ylim([35.858, 35.872])
plt.colorbar()
plt.show()
#plt.savefig('MudCreekDownslopeDisplacement_2.pdf')
###############################################################################
'''
#test:
azimuth_isce = [-270, -270, -270]
incidence_isce = [33, 33, 33]
length = np.sqrt(3**2+2**2)
az_rot = lp.rotate_azimuth(azimuth_isce, direction = 'cc')
t2p = lp.pol2cart(az_rot, incidence_isce, length )
p2t = lp.reverse_vector(t2p)
slope = [71.6, 71.6, 71.6]
aspect = [270, 270, 270]
asp_rot = lp.rotate_azimuth(aspect)
slope_vert = lp.slope_from_vertical(slope)
fall_line = lp.pol2cart(asp_rot, slope_vert, np.sqrt(1**2 + 3**2))
delta, a3, b3 = lp.compute_delta(fall_line, p2t)
los_def = [1,2,3]
surface_def = lp.los2def(los_def, delta)
'''
