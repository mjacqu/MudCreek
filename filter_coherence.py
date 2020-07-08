import sys
sys.path.append('/home/myja3483/isce_tools/MudCreek')
import numpy as np
import coherence_filter

coh_th = 0.35#threshold of mean coherence for filtering

tiff_path = '/net/tiampostorage/volume1/MyleneShare/Bigsur_desc/az1rng2/coherence/'
#tiff_path = '/net/tiampostorage/volume1/MyleneShare/Bigsur_asc/az1rng2/coherence/'

tiff_name = '*coherence.tif'
poly_path = '/home/myja3483/isce_tools/MudCreek/'
poly_name = 'ref_slope_large.geojson'

mv = coherence_filter.filt_coh(coh_th, tiff_path, tiff_name, poly_path, poly_name, write = True)
