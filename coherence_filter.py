import numpy
import os
from rasterstats import zonal_stats
import glob
import re
import datetime
from itertools import compress


def filt_coh (c, tiff_path, tiff_name, poly_path, poly_name, write = False):
    tiff_list = glob.glob(os.path.join(tiff_path, tiff_name))
    dates = [re.search(r'[0-9]{8}_[0-9]{8}', l).group(0) for l in tiff_list]
    stats = [zonal_stats(os.path.join(poly_path,poly_name), l)[0] for l in tiff_list]
    filter = [s['mean'] < c for s in stats]
    #generate list of dates to REMOVE
    remove_dates = numpy.sort(list(compress(dates, filter)))
    print('Coherence threshold: ' + str(c))
    if write == True:
        print('Writing ' + str(len(remove_dates)) + ' low coherence date pairs to file.')
        with open('low_coherence'+ str(c)+'.txt', 'w') as f:
            for item in remove_dates:
                f.write("%s\n" % item)
    else:
        print(str(len(remove_dates)) + ' pairs below ' + str(c) + ' coherence threshold:')
        print(remove_dates)
    return remove_dates
