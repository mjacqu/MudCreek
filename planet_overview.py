import numpy as np
import sys
sys.path.append('/Users/mistral/git_repos/ISCE')
import insarhelpers
import glob
import os
import rasterio
import matplotlib.pyplot as plt
from pyproj import Proj
from PIL import Image, ImageEnhance
import geopandas as gpd


im_path = '/Users/mistral/Documents/CUBoulder/Science/BigSur/data/Planet/'
#pre image
#im_fp = os.path.join(im_path,'MudCreekDec20_REOrthoTile_Explorer/files/1055620_2016-12-20_RE1_3A_Visual_clip.tif')
# post image
im_fp = os.path.join(im_path, 'MudCreekPost_REOrthoTile_Explorer/files/1055620_2017-06-14_RE1_3A_Visual_clip.tif')

src = rasterio.open(im_fp)
data = src.read()
gt = src.get_transform()
extent = gt[0],gt[0]+(src.width*gt[1]), gt[3]+(src.height*gt[5]), gt[3]

red = insarhelpers.normalize_rgb(data[0])
green = insarhelpers.normalize_rgb(data[1])
blue = insarhelpers.normalize_rgb(data[2])


planet_rgb = (np.dstack((red, green, blue))* 255.999).astype(np.uint8)
img = Image.fromarray(planet_rgb) # turn in to PIL image
brightness = ImageEnhance.Brightness(img)
b_factor = 1
planet_bright = brightness.enhance(b_factor)
contrast = ImageEnhance.Contrast(planet_bright)
c_factor = 1
planet_contrast = contrast.enhance(c_factor)

slide_poly = gpd.read_file('/Users/mistral/Documents/CUBoulder/Science/BigSur/before_after/slide_outline_overview.geojson')

fig, ax = plt.subplots(figsize = (8,8))
ax.imshow(planet_contrast, extent = extent)
gpd.plotting.plot_dataframe(slide_poly, ax = ax, edgecolor = 'k')
ax.set_ylim([3969000, 3971500])
ax.set_xlim([640550,642750])
ylabels = ['{:,.1f}'.format(y) for y in ax.get_yticks()/1000]
xlabels = ['{:,.1f}'.format(x) for x in ax.get_xticks()/1000]
ax.set_yticklabels(ylabels)
ax.set_xticklabels(xlabels)
ax.yaxis.set_major_locator(plt.MaxNLocator(6))
ax.xaxis.set_major_locator(plt.MaxNLocator(6))
ax.set_ylabel('y (km)')
ax.set_xlabel('x (km)')
#fig.show()
fig.savefig('mudcreek_post.pdf')
