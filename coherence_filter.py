import numpy
import os
from rasterstats import zonal_stats
import glob
import re
import datetime
from itertools import compress

coh_th = 0.8#threshold of mean coherence for filtering

tiff_path = '/Users/mistral/Documents/CUBoulder/Science/BigSur/before_after'
tiff_name = '*coherence.tif'

tiff_list = glob.glob(os.path.join(tiff_path, tiff_name))

poly_path = '/Users/mistral/Documents/CUBoulder/Science/BigSur/before_after'
poly_name = 'ref_slope_large.geojson'

dates = [re.search(r'[0-9]{8}_[0-9]{8}', l).group(0) for l in tiff_list]

stats = [zonal_stats(os.path.join(poly_path,poly_name), l)[0] for l in tiff_list]

filter = [s['mean'] < coh_th for s in stats]

#generate list of dates to REMOVE
remove_dates = list(compress(dates, filter))

with open('low_coherence.txt', 'w') as f:
    for item in remove_dates:
        f.write("%s\n" % item)
